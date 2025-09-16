from django.db import models

class Composer(models.Model):
    name = models.CharField(max_length=200)
    portrait_url = models.URLField()
    period = models.CharField(max_length=100)
    analyzed_works = models.IntegerField()
    analysis_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_intervals = models.IntegerField()
    polyphony_type = models.CharField(max_length=100)
    biography = models.TextField()

    def __str__(self):
        return self.name

class IntervalStat(models.Model):
    composer = models.ForeignKey(Composer, on_delete=models.CASCADE, related_name='interval_stats')
    interval_group = models.CharField(max_length=100)
    frequency = models.FloatField()
    std_dev = models.FloatField()

    def __str__(self):
        return f"{self.interval_group} for {self.composer.name}"