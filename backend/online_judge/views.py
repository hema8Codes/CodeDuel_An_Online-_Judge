import subprocess
import os
import uuid
import time
import psutil
import logging
from pathlib import Path
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from online_judge.models import Problems, TestCase, Submission
from online_judge.serializers import ProblemsListSerializer, ProblemsDetailSerializer, SubmissionSerializer
from online_judge.models import Problems,TestCase, Submission
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication



class ProblemsListAPIView(generics.ListAPIView):
    queryset = Problems.objects.all()
    serializer_class = ProblemsListSerializer

    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated]
    
class ProblemsDetailAPIView(generics.RetrieveAPIView):
    queryset = Problems.objects.all()
    serializer_class = ProblemsDetailSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
class UserSubmissionsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        problem_id = request.query_params.get('problem_id', None)

        if problem_id:
            try:
                problem = Problems.objects.get(id=problem_id)
            except Problems.DoesNotExist:
                return Response({'detail': 'Problem not found.'}, status=status.HTTP_404_NOT_FOUND)

            submissions = Submission.objects.filter(user=user, problem=problem)
        else:
            submissions = Submission.objects.filter(user=user)

        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExecuteCodeAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    # Define the logger at the class level
    logger = logging.getLogger(__name__)

    def post(self, request):
        lang = request.data.get("lang")
        problem_code = request.data.get("problem_code")
        code = request.data.get("code")

        if lang not in ["cpp", "py"]:
            return Response(
                {"error": "Invalid language"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve the problem using primary key
        problem = get_object_or_404(Problems, pk=problem_code)
        
        test_cases = TestCase.objects.filter(problem=problem)
        if not test_cases.exists():
            return Response(
                {"error": "No test cases found for this problem"}, status=status.HTTP_404_NOT_FOUND
            )

        output, verdicts, execution_time, memory_used = self.run_code(lang, code, test_cases)

        submission = Submission.objects.create(
            user=request.user,
            problem=problem,
            language=lang,
            verdict=" | ".join(verdicts),
            compiler_output=" | ".join(verdicts),
            test_case_results=[{"input": test_case.input, "output": test_case.output, "verdict": verdict}
                        for test_case, verdict in zip(test_cases, verdicts)],
            submitted_code=code,
            execution_time=execution_time,
            memory_used=memory_used
        )

        return Response(
            {"submission": {
                "verdicts": verdicts,
                "execution_time": execution_time,
                "memory_used": memory_used
            }},
            status=status.HTTP_200_OK,
        )

    def run_code(self, language, code, test_cases):
        try:
            project_path = Path(settings.BASE_DIR)
        except AttributeError as e:
            self.logger.error(f"Settings error: {str(e)}")
            return Response(
                {"error": f"Settings error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        directories = ["codes", "inputs", "outputs"]

        for directory in directories:
            dir_path = project_path / directory
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)

        codes_dir = project_path / "codes"
        inputs_dir = project_path / "inputs"
        outputs_dir = project_path / "outputs"

        unique = str(uuid.uuid4())

        code_file_name = f"{unique}.{language}"
        code_file_path = codes_dir / code_file_name

        with open(code_file_path, "w") as code_file:
            code_file.write(code)

        start_time = time.time()
        start_memory = psutil.Process(os.getpid()).memory_info().rss  # Start memory usage

        verdicts = []
        output_data = ""

        for test_case in test_cases:
            input_file_name = f"{unique}_{test_case.pk}.txt"
            output_file_name = f"{unique}_{test_case.pk}.txt"

            input_file_path = inputs_dir / input_file_name
            output_file_path = outputs_dir / output_file_name

            with open(input_file_path, "w") as input_file:
                input_file.write(test_case.input)

            with open(output_file_path, "w") as output_file:
                pass  # This will create an empty file

            if language == "cpp":
                executable_path = codes_dir / unique
                compile_result = subprocess.run(
                    ["clang++", str(code_file_path), "-o", str(executable_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                if compile_result.returncode != 0:
                    self.logger.error(f"Compilation Error: {compile_result.stderr.decode()}")
                    verdicts.append("Compilation Error")
                    continue

                with open(input_file_path, "r") as input_file:
                    with open(output_file_path, "w") as output_file:
                        execution_result = subprocess.run(
                            [str(executable_path)],
                            stdin=input_file,
                            stdout=output_file,
                            stderr=subprocess.PIPE,
                        )
                        if execution_result.returncode != 0:
                            self.logger.error(f"Runtime Error: {execution_result.stderr.decode()}")
                            verdicts.append("Runtime Error")
                            continue

            elif language == "py":
                with open(input_file_path, "r") as input_file:
                    with open(output_file_path, "w") as output_file:
                        execution_result = subprocess.run(
                            ["python3", str(code_file_path)],
                            stdin=input_file,
                            stdout=output_file,
                            stderr=subprocess.PIPE,
                        )
                        if execution_result.returncode != 0:
                            self.logger.error(f"Runtime Error: {execution_result.stderr.decode()}")
                            verdicts.append("Runtime Error")
                            continue

            with open(output_file_path, "r") as output_file:
                output_data = output_file.read()

            self.logger.debug(f"Test Case Input: {test_case.input}")
            self.logger.debug(f"Expected Output: {test_case.output}")
            self.logger.debug(f"Generated Output: {output_data.strip()}")

            reference_output = test_case.output.strip()
            generated_output = output_data.strip()

            verdict = "Accepted" if generated_output == reference_output else "Wrong Answer"
            verdicts.append(verdict)

        end_time = time.time()
        end_memory = psutil.Process(os.getpid()).memory_info().rss  # End memory usage

        # Calculate execution time and memory usage
        execution_time = end_time - start_time
        memory_used = (end_memory - start_memory) / (1024 * 1024)  # Convert bytes to MB

        return output_data, verdicts, execution_time, memory_used
