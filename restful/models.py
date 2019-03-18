import datetime
import uuid

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.
MAX_SIZE = 40


class RecordMixin(models.Model):
    # deleted flag
    is_deleted = models.BooleanField(default=False)
    # record time
    created_at = models.DateTimeField('created', auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Game(RecordMixin):
    STATUS = (
        ('PD', 'pending'),
        ('WN', 'won'),
        ('LT', 'lost'),
    )
    # pk
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # game data
    size_x = models.PositiveSmallIntegerField(validators=[
        MaxValueValidator(MAX_SIZE),
        MinValueValidator(1)
    ])
    size_y = models.PositiveSmallIntegerField(validators=[
        MaxValueValidator(MAX_SIZE),
        MinValueValidator(1)
    ])
    mine_num = models.PositiveSmallIntegerField(validators=[
        MaxValueValidator(MAX_SIZE * MAX_SIZE - 1),
        MinValueValidator(1)
    ])
    map_data = ArrayField(ArrayField(
        models.SmallIntegerField(), size=MAX_SIZE), size=MAX_SIZE, editable=False)
    player = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(
        max_length=2,
        choices=STATUS,
        default='PD',
    )
    snapshot = ArrayField(ArrayField(
        models.SmallIntegerField(), size=40, default=list), size=40, default=list)

    def __str__(self):
        return 'Game'
