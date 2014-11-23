from django.db import models


class Project(models.Model):
    pass

    class Meta:
        db_table = 'ctoria_project'


class Script(models.Model):
    project = models.ForeignKey(Project,null=True)
    title = models.CharField(max_length=120)
    author = models.CharField(max_length=60)
    description = models.CharField(max_length=512)
    date = models.DateField()
    version = models.CharField(max_length=30)

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = 'ctoria_script'


class Act(models.Model):
    script = models.ForeignKey(Script)
    title = models.CharField(max_length=120)
    description = models.CharField(max_length=256)

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = 'ctoria_act'


class Scene(models.Model):
    act = models.ForeignKey(Act)
    title = models.CharField(max_length=120)
    description = models.CharField(max_length=128)

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = 'ctoria_scene'


class Part(models.Model):
    scene = models.ForeignKey(Scene)
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=128)

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = 'ctoria_part'


class Content(models.Model):
    part = models.ForeignKey(Part)
    name = models.CharField(max_length=32)

    class Meta:
        db_table = 'ctoria_content'


class Item(models.Model):
    content = models.ForeignKey(Content, null=True)
    source = models.ManyToManyField('Source', through='ItemSource', null=True)
    name = models.CharField(max_length=32, null=True)
    MEDIA_TYPES = (('video', 'VIDEO'), ('audio', 'AUDIO'))
    media = models.CharField(max_length=30, choices=MEDIA_TYPES, default='video')

    class Meta:
        db_table = 'ctoria_item'


class ItemSource(models.Model):
    item = models.ForeignKey(Item)
    source = models.ForeignKey('Source')
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'ctoria_item_source'


class Line(models.Model):
    content = models.ForeignKey(Content, null=True)
    source = models.ManyToManyField('Source', through='LineSource', null=True)
    line = models.CharField(max_length=256)
    speaker = models.CharField(max_length=60, default='Narration')

    class Meta:
        db_table = 'ctoria_line'


class LineSource(models.Model):
    line = models.ForeignKey(Line)
    source = models.ForeignKey('Source')
    order = models.IntegerField(default=0)


    class Meta:
        db_table = 'ctoria_line_source'


class Group(models.Model):
    content = models.ForeignKey(Content, null=True)
    name = models.CharField(max_length=32, null=True)
    item = models.ManyToManyField('Item', null=True)
    line = models.ManyToManyField('Line', null=True)
    source = models.ManyToManyField('Source', through='GroupSource', null=True)

    class Meta:
        db_table = 'ctoria_group'


class GroupSource(models.Model):
    group = models.ForeignKey(Group)
    source = models.ForeignKey('Source')
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'ctoria_group_source'


class GroupLine(models.Model):
    group = models.ForeignKey(Group)
    line = models.ForeignKey(Line)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'ctoria_group_line'


class GroupItem(models.Model):
    group = models.ForeignKey(Group)
    item = models.ForeignKey(Item)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'ctoria_group_item'


class Type(models.Model):
    content = models.ForeignKey(Content, null=True)
    group = models.ForeignKey(Group, null=True)
    line = models.ForeignKey(Line, null=True)
    item = models.ForeignKey(Item, null=True)
    name = models.CharField(max_length=32)
    arguments = models.CharField(max_length=256)

    class Meta:
        db_table = 'ctoria_type'


class Source(models.Model):
    mime = models.CharField(max_length=32)
    file = models.CharField(max_length=80)
    size = models.IntegerField()
    duration = models.IntegerField()

    class Meta:
        db_table = 'ctoria_source'