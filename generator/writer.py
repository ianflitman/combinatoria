__author__ = 'ian'

from script import models
from random import randrange
from datetime import datetime
from enum import Enum
import json


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
        self.get_part(part_id)
        part = PartBox(part_id)
        self.parts.append(part)
        return part

    def get_part(self, part_id):
        for part in self.parts:
            if part.id == part_id:
                return part


class PartBox(object):

    def __init__(self, part_id):
        self.id = part_id
        self.contents = []

    def __iter__(self):
        iter(self.contents)

    def add_content(self, content_id):
        content = self.get_content(content_id)
        if content is None:
            content = ContentBox(content_id)
            self.contents.append(content)
            return content
        else:
            return

    def get_content(self, content_id):
        for content in self.contents:
            if content.id == content_id:
                return content


class ContentBox(object):

    def __init__(self, content_id):
        self.id = content_id
        self.sources = []

    def __iter__(self):
        iter(self.sources)

    def add_source(self, source_id, file):
        source = SourceBox(source_id, file)
        self.sources.append(source)

    def count(self):
        return len(self.sources)

class SourceBox(object):

    def __init__(self, source_id, file):
        self.id = source_id
        self.file = file

    def __iter__(self):
        iter(self)


class Scenario(object):

    def __init__(self, title):
        self.title = title
        self.id = models.Script.objects.get(title=self.title)
        self.script = ScriptBox()
        self.active_content = None


    def add_act(self, act_id):
        self.script.add_act(act_id)


    def add_scene(self, act_id, scene_id):
        self.script.get_act(act_id).add_scene(scene_id)


    def add_part(self, act_id, scene_id, part_id):
        self.script.get_act(act_id).get_scene(scene_id).add_part(part_id)


    def add_content(self, act_id, scene_id, part_id, content_id):
        self.active_content = self.script.get_act(act_id).get_scene(scene_id).get_part(part_id).add_content(content_id)


    def get_content(self, act_id, scene_id, part_id, content_id):
        self.active_content = self.script.get_act(act_id).get_scene(scene_id).get_part(part_id).get_content(content_id)
        return self.active_content


    def add_source(self, source_id, file):
        self.active_content.add_source(source_id, file)
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


    def add_content(self, content_id):
        boxes = self.get_act_scene_part(content_id)
        self.scenario.add_content(boxes[0], boxes[1], boxes[2], content_id)


    def get_content(self, content_id):
        boxes = self.get_act_scene_part(content_id)
        return self.scenario.get_content(boxes[0], boxes[1], boxes[2], content_id)


    def get_act_scene_part(self, content_id):
        act_id = models.Content.objects.get(id=content_id).part.scene.act.id
        scene_id = models.Content.objects.get(id=content_id).part.scene.id
        part_id = models.Content.objects.get(id=content_id).part.id
        return [act_id, scene_id, part_id]

    def init_content_ids(self):
        scene = models.Scene.objects.get(title=self.scene).id
        for part in models.Part.objects.filter(scene_id=scene):
            for content in models.Content.objects.filter(part_id=part.id):
                self.content_ids.append(content.id)


    def process(self):
        for content_id in self.content_ids:
            type =  models.Type.objects.filter(content_id=content_id).first()
            print(type.name)
            self.branch(type.name, content_id)

    # when id is None the scenario is written chronologically, when not None
    # a known selection is passed in for paired selection processing
    def branch(self, type_name, content_id, id=None):
        if type_name == 'SEQUENCE_SET':
            self.process_sequence_set(content_id)
        elif type_name == 'DEFAULT':
            self.process_default(content_id)
        elif type_name == 'ALTERNATIVE_FREE':
            self.process_alternative_free(content_id, id)
        elif type_name == 'ALTERNATIVE_COMPOUND':
            self.process_compound()
            pass
        elif type_name == 'ALTERNATIVE_PARENT':
            self.process_parent(content_id)
            pass
        elif type_name == 'ALTERNATIVE_PAIRED':
            self.process_paired(content_id)
        elif type_name == 'ALTERNATIVE_PAIRED_PARENT':
            self.process_paired_parent(content_id)
        elif type_name == 'ALTERNATIVE_PAIRED_MIXED':
            pass


    # def branch_by_id(self, type_name, id):
    #     if type_name == 'SEQUENCE_SET':
    #         pass
    #     elif type_name == 'DEFAULT':
    #         pass
    #     elif type_name == 'ALTERNATIVE_FREE':
    #         self.process_alternative_free_by_id(id)
    #     elif type_name == 'ALTERNATIVE_COMPOUND':
    #         pass
    #     elif type_name == 'ALTERNATIVE_PARENT':
    #         pass
    #     elif type_name == 'ALTERNATIVE_PAIRED':
    #         pass
    #     elif type_name == 'ALTERNATIVE_PAIRED_PARENT':
    #         pass
    #     elif type_name == 'ALTERNATIVE_PAIRED_MIXED':
    #         pass


    def process_sequence_set(self, content_id):
        sets = models.Group.objects.get(content_id=content_id, name='sets')
        set_groups = models.GroupContainer.objects.filter(container=sets)# short, med, long
        #set_groups = models.Item.objects.filter(group=sets.id).exclude(name='library')
        selected_set = set_groups[self.random(len(set_groups))] #shor or med or long
        seqs = models.GroupContainer.objects.filter(container_id=selected_set.group_id)
        #seqs = models.Group.objects.filter(item=selected_set)
        selected_seq = seqs[self.random(len(seqs))]
        sources = models.Group.objects.get(id=selected_seq.group_id).source.all()
        #self.add_content(content_id)
        if len(sources) == 0:
            print('empty seq')
        for source in sources:
            print(source.file)
            self.add_content(content_id)
            self.scenario.add_source(source.id, source.file)

        pass


    def process_default(self, content_id):
        sources = models.Line.objects.get(content=content_id).source.all()
        source = sources[self.random(len(sources))]
        self.add_content(content_id)
        self.scenario.add_source(source.id, source.file)
        print(source.file)
        pass


    def process_alternative_free(self, content_id, alt_id):
        if alt_id is None:
            options = models.Group.objects.get(content=content_id).line.all()
        else:
            options = models.Group.objects.get(id=alt_id).line.all()

        option = options[self.random(len(options))]
        sources = models.Line.objects.get(id=option.id).source.all()
        source = sources[self.random(len(sources))]
        self.add_content(content_id)
        self.scenario.add_source(source.id, source.file)
        print(source.file)

    # def process_alternative_free_by_id(self, content_id, alt_id):
    #     options = models.Group.objects.get(id=alt_id).line.all()
    #     option = options[self.random(len(options))]
    #     sources = models.Line.objects.get(id=option.id).source.all()
    #     source = sources[self.random(len(sources))]
    #     self.add_content(content_id)
    #     self.scenario.add_source(source.id, source.file)
    #     print(source.file)

    def process_paired(self, content_id):
        type_arguments = json.loads(models.Content.objects.get(id=content_id).type_set.get().arguments)
        print(type_arguments[u'pos'])
        if type_arguments[u'pos'] == 1:
            self.process_alternative_free(content_id, None)
        else:
            print(type_arguments['prev'])
            prev_content = self.get_content(type_arguments['prev'])

            pass


    def process_parent(self, content_id):
        children = models.Type.objects.filter(content_id=content_id)[1:]
        chosen = children[self.random(len(children))]
        print(chosen.name)
        self.branch(chosen.name, chosen.content_id)
        pass

    def process_paired_parent(self, content_id):
        type_arguments = json.loads(models.Content.objects.get(id=content_id).type_set.get(name='ALTERNATIVE_PAIRED_PARENT').arguments)
        print(type_arguments[u'pos'])
        if type_arguments[u'pos'] == 1:
            self.process_alternative_free(content_id)
        else:
            previous = int(type_arguments['prev'])
            print(previous)
            prev_lines_set = [line.line for line in models.Content.objects.get(id=previous).line_set.all()]
            prev_src_id = self.get_content(previous).sources[0].id
            chosen_line = models.Line.objects.get(source=prev_src_id).line
            print(chosen_line)
            index = prev_lines_set.index(chosen_line)
            alt_chosen = list(models.Type.objects.filter(content_id=content_id)[1:][index:index+1])[0]

            print(alt_chosen.name)
            print(alt_chosen.id)
            self.branch(alt_chosen.name, content_id, alt_chosen.group_id)
            print('what')


            pass
        pass


    def random(self, number):
        if number == 1:
            return 0
        else:
            return randrange(0, number-1)


    def process_compound(self):
        pass

    def get_parts(self):
        pass






write_script = Writer('jane',scene="Married too long")
#write_script = Writer('jane',scene="Old films, new endings")
#write_script = Writer('jane',scene="Bedtime stories")