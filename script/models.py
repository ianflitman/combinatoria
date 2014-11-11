from django.db import models


class Project(models.Model):
    pass


class Script(models.Model):
    project = models.ForeignKey(Project,null=True)
    title = models.CharField(max_length=120)
    author = models.CharField(max_length=60)
    description = models.CharField(max_length=512)
    date = models.DateField()
    version = models.CharField(max_length=30)

    def __unicode__(self):
        return self.title


class Act(models.Model):
    script = models.ForeignKey(Script)
    title = models.CharField(max_length=120)
    description = models.CharField(max_length=256)

    def __unicode__(self):
        return self.title


class Scene(models.Model):
    act = models.ForeignKey(Act)
    title = models.CharField(max_length=120)
    description = models.CharField(max_length=128)

    def __unicode__(self):
        return self.title


class Part(models.Model):
    scene = models.ForeignKey(Scene)
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=128)

    def __unicode__(self):
        return self.title


class Content(models.Model):
    part = models.ForeignKey(Part)
    name = models.CharField(max_length=32)


class Item(models.Model):
    content = models.ForeignKey(Content, null=True)
    source = models.ManyToManyField('Source', null=True)
    name = models.CharField(max_length=32, null=True)
    MEDIA_TYPES = (('video', 'VIDEO'), ('audio', 'AUDIO'))
    media = models.CharField(max_length=30, choices=MEDIA_TYPES, default='video')


class Line(models.Model):
    content = models.ForeignKey(Content, null=True)
    source = models.ManyToManyField('Source', null=True)
    line = models.CharField(max_length=256)
    speaker = models.CharField(max_length=60, default='Narration')


class Group(models.Model):
    content = models.ForeignKey(Content, null=True)
    name = models.CharField(max_length=32, null=True)
    item = models.ManyToManyField('Item', null=True)

    line = models.ManyToManyField('Line', null=True)
    source = models.ManyToManyField('Source', null=True)
    #source = models.ForeignKey('Source', null=True)

    #class Meta():
    #    order_with_respect_to = 'source'


class Type(models.Model):
    content = models.ForeignKey(Content, null=True)
    group = models.ForeignKey(Group, null=True)
    line = models.ForeignKey(Line, null=True)
    item = models.ForeignKey(Item, null=True)
    name = models.CharField(max_length=32)
    arguments = models.CharField(max_length=32)


class Source(models.Model):
    mime = models.CharField(max_length=32)
    file = models.CharField(max_length=80)
    size = models.IntegerField()
    duration = models.IntegerField()