__author__ = 'ian'

from script import models
from random import randrange
from datetime import datetime
from enum import Enum


class Cursor(Enum):
    ACT = 0
    SCENE = 1
    PART = 2
    CONTENT = 3


class ScriptBox(object):

    def __init__(self):
        self.date = datetime.now()
        self.acts = []

    def __iter__(self):
        iter(self.acts)

    def add_act(self, act_id):
        #check not added already
        for act in self.acts:
            if act.id == act_id:
                return act

        act = ActBox(act_id)
        self.acts.append(act)
        return act

    def get_act(self, act_id):
        for act in self.acts:
            if act.id == act_id:
                return act


class ActBox(object):

    def __init__(self, id):
        self.id = id
        self.scenes = []

    def __iter__(self):
        iter(self.scenes)

    def add_scene(self, scene_id):
        #check not added already
        for scene in self.scenes:
            if scene.id == scene_id:
                return scene

        scene = SceneBox(scene_id)#, self.id)
        self.scenes.append(scene)
        return scene

    def get_scene(self,scene_id):
        for scene in self.scenes:
            if scene.id == scene_id:
                return scene

class SceneBox(object):

    def __init__(self, scene_id): #, act_id):
        self.id = scene_id
        #self.act_id = act_id
        self.parts = []

    def __iter__(self):
        iter(self.parts)

    def add_part(self, part_id):
        part = PartBox(part_id)#, self.id)
        self.parts.append(part)
        return part

    def get_part(self, part_id):
        for part in self.parts:
            if part.id == part_id:
                return part

class PartBox(object):

    def __init__(self, part_id):#, scene_id):
        self.id = part_id
        #self.scene_id = scene_id
        self.contents = []

    def __iter__(self):
        iter(self.contents)

    def add_content(self, content_id):
        content = ContentBox(content_id)#, self.id)
        self.contents.append(content)

    def get_content(self, content_id):
        for content in self.contents:
            if content.id == content_id:
                return content


class ContentBox(object):

    def __init__(self, content_id):#, part_id):
        self.id = content_id
        #self.part_id = part_id
        self.sources = []

    def __iter__(self):
        iter(self.sources)

    def add_source(self, source_id, file):
        source = SourceBox(self.id, source_id, file)
        self.sources.append(source)

    def count(self):
        return len(self.sources)

class SourceBox(object):

    def __init__(self, source_id, file):
        #self.content_id = content_id
        self.id = source_id
        self.file = file

    def __iter__(self):
        iter(self)


class Scenario(object):

    def __init__(self, title):
        self.title = title
        self.id = models.Script.objects.get(title=self.title)
        self.script = ScriptBox()
        self.position = [None, None, None, None]
        self.active_content = None


    def add_act(self, act_id):
        self.script.add_act(act_id)

    def add_scene(self, act_id, scene_id):
        self.script.get_act(act_id).add_scene(scene_id)

    def add_part(self, act_id, scene_id, part_id):
        self.script.get_act(act_id).get_scene(scene_id).add_part(part_id)

    def add_content(self, act_id, scene_id, part_id, content_id):
        self.script.get_act(act_id).get_scene(scene_id).get_part(part_id).add_content(content_id)

    def set_active_content(self, act_id, scene_id, part_id, content_id):
        self.active_content = self.script.get_act(act_id).get_scene(scene_id).get_part(part_id).get_content(content_id)

    def add_source(self):
        pass


    def __iter__(self):
        return iter(self)


class Writer(object):

    def __init__(self, script, act=None, scene=None, part=None):
        self.script = script
        self.act = act
        self.scene = scene
        self.scenario = Scenario(script)
        self.add_scenario_structure()
        self.content_ids = []
        self.init_content_ids()
        self.process()


    def add_scenario_structure(self):
        act_id = models.Scene.objects.get(title=self.scene).act_id
        self.scenario.add_act(act_id)
        scenes = models.Scene.objects.filter(title=self.scene)
        for scene in scenes:
            self.scenario.add_scene(act_id, scene.id)
            for part in models.Part.objects.filter(scene_id=scene.id):
                self.scenario.add_part(act_id, scene.id, part.id)

        pass


    def get_path_to_content(self, content_id):
        act_id = models.Content.objects.get(id=content_id).part.scene.act.id
        scene_id = models.Content.objects.get(id=content_id).part.scene.id
        part_id = models.Content.objects.get(id=content_id).part.id
        return [act_id, scene_id, part_id, content_id]


    def init_content_ids(self):
        scene = models.Scene.objects.get(title=self.scene).id
        for part in models.Part.objects.filter(scene_id=scene):
            print(part.id)
            for content in models.Content.objects.filter(part_id=part.id):
                self.content_ids.append(content.id)
                print(content.id)


    def process(self):
        for content_id in self.content_ids:
            type =  models.Type.objects.filter(content_id=content_id).first()
            print(type.name)
            self.branch(type.name, content_id)


    def branch(self, type_name, content_id):
        if type_name == 'SEQUENCE_SET':
            self.process_sequence_set(content_id)
            #sets = models.Group.objects.get()

        elif type_name == 'DEFAULT':
            pass
        elif type_name == 'ALTERNATIVE_FREE':
            pass
        elif type_name == 'ALTERNATIVE_COMPOUND':
            self.process_compound()
            pass
        elif type_name == 'ALTERNATIVE_PARENT':
            self.process_parent(content_id)
            pass
        elif type_name == 'ALTERNATIVE_PAIRED':
            pass
        elif type_name == 'ALTERNATIVE_PAIRED_PARENT':
            pass
        elif type_name == 'ALTERNATIVE_PAIRED_MIXED':
            pass



    def process_sequence_set(self, content_id):
        sets = models.Group.objects.get(content_id=content_id, name='sets')
        set_groups = models.Item.objects.filter(group=sets.id)
        selected_set = set_groups[self.random(len(set_groups))]#short medium or long
        seqs = models.Group.objects.filter(item=selected_set)
        selected_seq = seqs[self.random(len(seqs))]
        #sources = models.Source.objects.filter(group=selected_seq.id)
        sources = models.Group.objects.get(id=selected_seq.id).source.all()

        #self.scenario.set_active_content()
        for source in sources:
            print(source.file)
            self.get_path_to_content(content_id)

            pass


        pass




    def process_alternative_free(self):
        pass

    def process_parent(self, content_id):
        children =  models.Type.objects.filter(content_id=content_id)[1:]
        #chosen = choice(children)
        chosen = children[self.random(children.__len__())]
        print(chosen.name)
        self.branch(chosen.name, chosen.content_id)
        pass


    def random(self, number):
        return randrange(0, number-1) #random()*number


    def process_compound(self):
        pass

    def get_parts(self):
        pass


    def get_content(self):
        pass



#write_script = Writer('jane',scene="Married too long")
#write_script = Writer('jane',scene="Old films, new endings")
write_script = Writer('jane',scene="Bedtime stories",act="conversations")