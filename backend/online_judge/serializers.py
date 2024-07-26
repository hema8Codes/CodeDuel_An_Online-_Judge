from rest_framework import serializers
from online_judge.models import Problems, Submission
    
class ProblemsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problems
        exclude = ['created_at', 'updated_at','statement_description', 'base_function_code','problem_visualization_illustration','constraint_description','language']

class CppBaseFunctionCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problems
        fields = ['base_function_code']  

class PythonBaseFunctionCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problems
        fields = ['base_function_code']  

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'problem', 'language', 'verdict', 'compiler_output', 'test_case_results', 'submitted_code', 'submitted_at', 'execution_time', 'memory_used']

        
class ProblemsDetailSerializer(serializers.ModelSerializer):
    base_function_code = serializers.SerializerMethodField()
    
    class Meta:
        model = Problems
        exclude = ['created_at', 'updated_at']
    
    def get_base_function_code(self, obj):
        if obj.language == 'C++':
            return obj.base_function_code.get('C++', '')
        elif obj.language == 'Python':
            return obj.base_function_code.get('Python', '')
        return ''
        