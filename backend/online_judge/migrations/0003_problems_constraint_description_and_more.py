# Generated by Django 5.0.7 on 2024-07-23 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('online_judge', '0002_alter_problems_problem_visualization_illustration'),
    ]

    operations = [
        migrations.AddField(
            model_name='problems',
            name='constraint_description',
            field=models.TextField(default='', max_length=500),
        ),
        migrations.DeleteModel(
            name='ProblemConstraints',
        ),
    ]
