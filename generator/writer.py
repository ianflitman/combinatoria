__author__ = 'ian'

from script import models
from random import randrange
from datetime import datetime
from enum import Enum
import json
import django

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

    def __repr__(self):
        return {id: self.id}


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

    def __repr__(self):
        return {'id': self.id}

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
            return content

    def get_content(self, content_id):
        for content in self.contents:
            if content.id == content_id:
                return content

    def __repr__(self):
        return str(self.id)

class ContentBox(object):

    def __init__(self, content_id):
        self.id = content_id
        self.sources = []
        self.lines = []

    def __iter__(self):
        iter(self.sources)

    def add_source(self, source_id, file):
        source = SourceBox(source_id, file)
        self.sources.append(source)

    def count(self):
        return len(self.sources)

    def __repr__(self):
        return str(self.id)

class SourceBox(object):

    def __init__(self, source_id, file):
        self.id = source_id
        self.file = file

    def __iter__(self):
        iter(self)

    def __repr__(self):
        return str(self.id)


class Scenario(object):

    def __init__(self, title):
        self.title = title
        self.id = models.Script.objects.get(title=self.title)
        self.script = ScriptBox()
        self.active_content = None
        #self.json


    def add_act(self, act_id):
        self.script.add_act(act_id)


    def add_scene(self, act_id, scene_id):
        self.script.get_act(act_id).add_scene(scene_id)


    def add_part(self, act_id, scene_id, part_id):
        self.script.get_act(act_id).get_scene(scene_id).add_part(part_id)


    def add_content(self, act_id, scene_id, part_id, content_id):
        self.active_content = self.script.get_act(act_id).get_scene(scene_id).get_part(part_id).add_content(content_id)


    def add_line(self, line_id):
        self.active_content.lines.append(line_id)


    def get_content(self, act_id, scene_id, part_id, content_id):
        self.active_content = self.script.get_act(act_id).get_scene(scene_id).get_part(part_id).get_content(content_id)
        return self.active_content


    def add_source(self, source_id, file):
        self.active_content.add_source(source_id, file)


    def __iter__(self):
        return iter(self)


    def line_iter(self):
        for act in self.script.acts:
            for scene in act.scenes:
                for part in scene.parts:
                    for content in part.contents:
                        yield (content.id, content.lines, [source.id for source in content.sources])

    def json_scenario(self):
        return json.dumps(self.script.acts)


class Writer(object):

    def __init__(self, script, act=None, scene=None, part=None):
        django.setup()
        self.script = script
        self.act = act
        self.scene = scene
        self.html = ''
        self.json = ''
        self.scenario = Scenario(script)
        self.add_scenario_structure()

        #self.content_ids = []
        #self.init_content_ids()
        self.process()
        self.write_scenario()


    def add_scenario_structure(self):
        self.json = {'script': {'meta':{'name': self.script},
                                'acts':[]}
        }

        act_id = models.Scene.objects.get(title=self.scene).act_id
        #act_id = models.Scene.objects.get(title=self.scene).objects.values('act_id','act_title')
        #act_id = models.Scene.objects.filter(title=self.scene).values('act_id','act_title')

        self.scenario.add_act(act_id)
        #self.json['script']['acts'].append({'name': models.Act.objects.get(pk=act_id).title, 'scenes':[]})

        #print(json.dumps(self.json))

        scenes = models.Scene.objects.filter(title=self.scene)

        for scene_counter, scene in enumerate(scenes):
            print('scene count {0}'.format(scene_counter))
            self.scenario.add_scene(act_id, scene.id)
            self.json['script']['acts'][0]['scenes'].append({'title': scene.title, 'parts':[]})
            print(json.dumps(self.json))
            for part_counter, part in enumerate(models.Part.objects.filter(scene_id=scene.id)):
                self.scenario.add_part(act_id, scene.id, part.id)
                print('part count {0}'.format(part_counter))
                self.json['script']['acts'][0]['scenes'][scene_counter]['parts'].append({'name': part.name, 'content':[]})
        print(json.dumps(self.json))

    def add_content(self, content_id):
        boxes = self.get_act_scene_part(content_id)
        self.scenario.add_content(boxes[0], boxes[1], boxes[2], content_id)

    def add_line(self, line_id):
        self.scenario.add_line(line_id=line_id)


    def get_content(self, content_id):
        boxes = self.get_act_scene_part(content_id)
        return self.scenario.get_content(boxes[0], boxes[1], boxes[2], content_id)


    def get_act_scene_part(self, content_id):
        act_id = models.Content.objects.get(id=content_id).part.scene.act.id
        scene_id = models.Content.objects.get(id=content_id).part.scene.id
        part_id = models.Content.objects.get(id=content_id).part.id
        return [act_id, scene_id, part_id]

    def scenario_content_ids(self):
        scene = models.Scene.objects.get(title=self.scene).id
        for part in models.Part.objects.filter(scene_id=scene):
            for content in models.Content.objects.filter(part_id=part.id):
                #self.content_ids.append(content.id)
                yield content.id


    def process(self):
        for content_id in self.scenario_content_ids(): #self.content_ids:
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
            self.process_compound(content_id, id)
        elif type_name == 'ALTERNATIVE_PARENT':
            self.process_parent(content_id)
        elif type_name == 'ALTERNATIVE_PAIRED':
            self.process_paired(content_id)
        elif type_name == 'ALTERNATIVE_PAIRED_PARENT':
            self.process_paired_parent(content_id)
        elif type_name == 'ALTERNATIVE_PAIRED_MIXED':
            pass


    def process_sequence_set(self, content_id):
        sets = models.Group.objects.get(content_id=content_id, name='sets')
        #print(models.Line.objects.get(content_id=content_id).id)
        set_groups = models.GroupContainer.objects.filter(container=sets)# short, med, long
        #set_groups = models.Item.objects.filter(group=sets.id).exclude(name='library')
        selected_set = set_groups[self.random(len(set_groups))] #shor or med or long
        seqs = models.GroupContainer.objects.filter(container_id=selected_set.group_id)
        #seqs = models.Group.objects.filter(item=selected_set)
        selected_seq = seqs[self.random(len(seqs))]
        sources = models.Group.objects.get(id=selected_seq.group_id).source.all()
        self.add_content(content_id)
        self.add_line(models.Line.objects.get(content_id=content_id).id)

        if len(sources) == 0:
            print('empty seq')
        for source in sources:
            print(source.file)
            #self.add_content(content_id)
            self.scenario.add_source(source.id, source.file)

        pass


    def process_default(self, content_id):
        sources = models.Line.objects.get(content=content_id).source.all()
        source = sources[self.random(len(sources))]
        self.add_content(content_id)
        self.add_line(models.Line.objects.get(content_id=content_id).id)
        self.scenario.add_source(source.id, source.file)
        print(source.file)
        #print(source.l)
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
        self.add_line(option.id)
        self.scenario.add_source(source.id, source.file)
        print(source.file)


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
        print(chosen.name, chosen.content_id, chosen.id)
        self.branch(chosen.name, chosen.content_id, chosen.id)
        pass

    def process_paired_parent(self, content_id):
        type_arguments = json.loads(models.Content.objects.get(id=content_id).type_set.get(name='ALTERNATIVE_PAIRED_PARENT').arguments)
        print(type_arguments[u'pos'])
        if type_arguments[u'pos'] == 1:
            self.process_alternative_free(content_id)
        else:
            previous = int(type_arguments['prev'])
            print(previous)
            prev_type = models.Type.objects.get(content_id=previous)
            print(prev_type.name)
            # this code assumes that the previous choice has one source attached to it
            # and has a line of description or dialogue
            # what happens when the prev one is also a parent?
            prev_src_id = self.get_content(previous).sources[0].id
            prev_src = models.Source.objects.get(id=prev_src_id)

            prev_alt = models.Group.objects.get(id=prev_type.group_id)
            line = models.LineSource.objects.get(source = prev_src).line
            index = models.GroupLine.objects.get(group=prev_alt, line=line).order
            alt_chosen = models.GroupContainer.objects.get(container=models.Group.objects.get(content_id=content_id, name__exact='alternative_paired_parent'), order=index).group

            print(alt_chosen.name)
            print(alt_chosen.id)
            print(models.Type.objects.get(group_id=alt_chosen.id).name)
            self.branch(models.Type.objects.get(group_id=alt_chosen.id).name, content_id, alt_chosen.id)


    def random(self, number):
        if number == 1:
            return 0
        else:
            return randrange(0, number-1)


    def process_compound(self, content_id, alt_id):
        #compound = models.Group.objects.filter(content_id=content_id)
        if alt_id is None:
            compound = models.Group.objects.get(content=content_id)
        else:
            compound = models.Type.objects.get(id=alt_id).group
            default = models.GroupLine.objects.filter(group=compound, order=0).get().line
            print(default.line)
            print(default.id)


        sources = models.Line.objects.get(id=default.id).source.all()
        #sources = models.LineSource.objects.filter(line=default).source
        source = sources[self.random(len(sources))]
        self.add_content(content_id)
        self.add_line(default.id)
        #self.add_line(models.Line.objects.get(content_id=default.id).id)
        self.scenario.add_source(source.id, source.file)


        options = models.GroupLine.objects.filter(group=compound)[1:]
        option = options[self.random(len(options))]
        sources = models.Line.objects.get(id=option.id).source.all()
        source = sources[self.random(len(sources))]
        self.add_content(content_id)
        self.add_line(option.line_id)
        self.scenario.add_source(source.id, source.file)
        pass


    def get_parts(self):
        pass


    def write_scenario(self):
        for x in self.scenario.line_iter():
            for line in x[1]:
                self.html += models.Line.objects.get(pk=line).speaker + ': ' + models.Line.objects.get(pk=line).line + '<br>'#''.join((models.Line.objects.get(pk=line).speaker, ': ', models.Line.objects.get(pk=line).line + '<br>'))
                print(models.Line.objects.get(pk=line).speaker + ': ' + models.Line.objects.get(pk=line).line)

        #json_script = self.scenario.json_scenario()#json.dumps(self.scenario.script)
        self.scenario_ui_json()
        #print(json.load(json_script))
        return self.html

    def scenario_ui_json(self):
        scenario_json = json.dumps({'script': {
                                         'meta': {},
                                         'acts':[{
                                             'scenes':[{
                                                 'parts': [{
                                                     'name':'',
                                                     'content:' :[{
                                                         'type':'',
                                                         'data':{}
                                                     }]
                                                 }]
                                             }]
                                         }]
                                    },
                                })
        print(scenario_json)




write_script = Writer('jane',scene="marriedtoolong")
#write_script = Writer('jane',scene="Old films, new endings")
#write_script = Writer('jane',scene="Bedtime stories")