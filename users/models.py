from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError

# Qualification creation    
class Qualification(models.Model):
    name = models.CharField(max_length=100, unique=True)
    saqa_id = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - SAQA ID: {self.saqa_id}"
    
# User creation   
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('assessor_dev', 'Assessor (Developer)'),
        ('moderator', 'Moderator (Developer)'),
        ('qcto', 'QCTO Validator'),
        ('etqa', 'ETQA'),
        ('learner', 'Learner'),  
        ('assessor_marker', 'Assessor (Marker)'),
        ('internal_mod', 'Internal Moderator'),
        ('external_mod', 'External Moderator (QALA)'),
    ]

    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='learner')
    qualification = models.ForeignKey(
        Qualification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'  # Added for reverse lookup
    )
    email = models.EmailField(unique=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(default=now)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    qualification_updated_at = models.DateTimeField(null=True, blank=True)  # New field
    last_updated_at = models.DateTimeField(auto_now=True)  # New field

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        """Track qualification changes"""
        if self.pk:  # Only for existing users
            original = CustomUser.objects.get(pk=self.pk)
            if original.qualification != self.qualification:
                self.qualification_updated_at = now()
        super().save(*args, **kwargs)

    def can_create_questions(self):
        """Check if user can create/edit questions"""
        return self.role in ['admin', 'assessor_dev', 'moderator']   
    
    def can_moderate_questions(self):
        """Check if user can moderate questions"""
        return self.role in ['admin', 'moderator', 'internal_mod', 'external_mod']

    class Meta:
        ordering = ['-created_at']

# model to store and create exam papers         

class ExaminationPaper(models.Model):
    """Main model for storing examination papers"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    qualification = models.ForeignKey(
        Qualification, 
        on_delete=models.CASCADE, 
        related_name='examination_papers'
    )
    paper_number = models.CharField(max_length=10)  # Free-text field
    total_marks = models.PositiveIntegerField()
    
    # Status and workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # User tracking
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_papers')
    reviewed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_papers')
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_papers')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Version control
    version = models.CharField(max_length=10, default='1.0')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['qualification', 'paper_number', 'version']
        ordering = ['qualification', 'paper_number', '-version']
        permissions = [
            ('can_review_papers', 'Can review examination papers'),
            ('can_approve_papers', 'Can approve examination papers'),
            ('can_publish_papers', 'Can publish examination papers'),
        ]
    
    def __str__(self):
        return f"{self.qualification.name} - {self.paper_number} v{self.version} (SAQA: {self.qualification.saqa_id})"
    
    @property
    def saqa_id(self):
        """Access the SAQA ID through the qualification relationship"""
        return self.qualification.saqa_id
    
    def get_total_questions(self):
        return self.questions.count()
    
    def get_calculated_marks(self):
        return sum(q.total_marks for q in self.questions.all())        

# model to create questions for exam papers 
class Question(models.Model):
    """Model for storing individual questions"""
    QUESTION_TYPES = [
        ('case_study', 'Case Study'),
        ('standard_answer', 'standard answer'),
        ('true_false', 'True or False'),
        ('multiple_choice', 'Multiple Choice'),
        # ('matching', 'Matching'),
        # ('diagram', 'Diagram/Drawing'),
        # ('checklist', 'Checklist'),
        # ('short_answer', 'Short Answer'),
        # ('essay', 'Essay'),
    ]
    
    # DIFFICULTY_LEVELS = [
    #     ('easy', 'Easy'),
    #     ('medium', 'Medium'),
    #     ('hard', 'Hard'),
    # ]
    
    paper = models.ForeignKey(ExaminationPaper, on_delete=models.CASCADE, related_name='questions')
    question_number = models.CharField(max_length=20, help_text="e.g., 1.1.1, 2.1.4")
    #title = models.CharField(max_length=500)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    #difficulty_level = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, default='medium')
    total_marks = models.PositiveIntegerField()
    
    # Question content
    question_text = models.TextField(help_text="Main question text")
    case_study_text = models.TextField(blank=True, help_text="Case study context (if applicable)")
    instructions = models.TextField(blank=True, help_text="Specific instructions for this question")
    
    # Marking information
    #marking_allocation = models.TextField(blank=True, help_text="How marks are distributed across sub-questions")
    #marking_notes = models.TextField(blank=True, help_text="Additional marking guidance for assessors")
    #sample_answer = models.TextField(blank=True, help_text="Sample answer or marking rubric")
    
    # Learning outcomes and assessment criteria
    #learning_outcome = models.TextField(blank=True, help_text="What learning outcome this question assesses")
    #assessment_criteria = models.TextField(blank=True, help_text="Specific assessment criteria")
    
    # User tracking
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_questions')
    reviewed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_questions')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Ordering and status
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['paper', 'order']
        unique_together = ['paper', 'question_number']
        permissions = [
            ('can_review_questions', 'Can review questions'),
            ('can_approve_questions', 'Can approve questions'),
        ]
    
    def __str__(self):
        return f"{self.paper} - Q{self.question_number}: {self.title[:50]}"
    
    def get_sub_questions_count(self):
        return self.sub_questions.count()
    
    def get_calculated_marks(self):
        """Calculate marks from sub-questions if they exist"""
        sub_marks = sum(sq.marks for sq in self.sub_questions.all())
        return sub_marks if sub_marks > 0 else self.total_marks        

#  model to create sub questions linking with the questions model above       

class SubQuestion(models.Model):
    """Model for storing sub-questions within a main question"""
    parent_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='sub_questions')
    sub_number = models.CharField(max_length=10, help_text="e.g., 1, 2, a, b")
    question_text = models.TextField()
    marks = models.PositiveIntegerField()
    order = models.PositiveIntegerField(default=1)
    
    # For specific question types
    is_true_false = models.BooleanField(default=False)
    correct_answer = models.CharField(max_length=50, blank=True, help_text="For T/F or short answer questions")
    explanation = models.TextField(blank=True, help_text="Explanation of correct answer")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['parent_question', 'order']
        unique_together = ['parent_question', 'sub_number']
    
    def __str__(self):
        return f"{self.parent_question.question_number}.{self.sub_number}"

# for storing multiple choice questions linking to sub question model   
class MultipleChoiceOption(models.Model):
    """Model for storing multiple choice options"""
    sub_question = models.ForeignKey(SubQuestion, on_delete=models.CASCADE, related_name='mc_options')
    option_letter = models.CharField(max_length=1, help_text="A, B, C, D")
    option_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True, help_text="Why this option is correct/incorrect")
    order = models.PositiveIntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sub_question', 'order']
        unique_together = ['sub_question', 'option_letter']
    
    def __str__(self):
        return f"{self.sub_question} - Option {self.option_letter}"    
    
# model for storing true and false questions linked to subquestions model
class TrueFalseStatement(models.Model):
    """Model for storing true/false statements"""
    sub_question = models.ForeignKey(SubQuestion, on_delete=models.CASCADE, related_name='tf_statements')
    statement_number = models.PositiveIntegerField()
    statement_text = models.TextField()
    is_true = models.BooleanField()
    explanation = models.TextField(blank=True, help_text="Explanation of why this is true/false")
    marks = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sub_question', 'order']
        unique_together = ['sub_question', 'statement_number']
    
    def __str__(self):
        return f"{self.sub_question} - Statement {self.statement_number}"    