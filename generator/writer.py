__author__ = 'ian'
from script import models
from random import choice, random, randrange

class Scenario(object):

    def __init__(self, script, acts):
        self.script = script
        self.acts = []
        self.current_act = -1
        self.current_scene = -1
        self.current_part = -1

    def __iter__(self):
        for act in self.acts:
            for scene in act:
                for part in scene:
                    return part.__iter__()


    def acts(self):
        return iter(self.acts)

    def scenes(self, act=None):
        if act is None:
            return self.acts[self.current_act].__iter__()
        else:
            return self.acts[act].__iter__()

    def parts(self, scene=None, act=None):
        if act is None:
            if scene is None:
                return self.acts[self.current_act][self.current_scene].__iter__()
            else:
                return self.acts[self.current_act][scene].__iter__()
        else:
            return self.acts[act][scene].__iter__()

    def contents(self, part=None, scene=None, act=None):
        if act is None:
            if scene is None:
                if part is None:
                    return self.acts[self.current_act][self.current_scene][self.current_part].__iter__()
                else:
                    return self.acts[self.current_act][self.current_scene][part].__iter__()
            else:
                 return self.acts[self.current_act][scene][part].__iter__()
        else:
            return self.acts[act][scene][part].__iter__()


class Act(object):

    def __init__(self, act, scenes):
        self.act_id = act
        self.scenes = scenes
        pass

    def __iter__(self):
        iter(self.scenes)

class Scene(object):

    def __init__(self, scene, parts):
        self.scene_id = scene
        self.parts = parts


    def __iter__(self):
        iter(self.parts)

class Part(object):

    def __init__(self, part, contents):
        self.part_id = part
        self.contents = contents

    def __iter__(self):
        iter(self.contents)


# class Unit(object):
#
#     def __init__(self, address):
#         self.address = address
#         self.files = []

class Address(object):

    def __init__(self, dict_val):
        self.act = dict_val['act']
        self.scene = dict_val['scene']
        self.part = dict_val['part']
        self.content = dict_val['content']


class Writer(object):

    def __init__(self, script, act=None, scene=None, part=None):
        self.script = script
        self.act = act
        self.scene = scene
        self.part = part
        self.content_ids = []
        self.init_content_ids()
        self.process()


    def select_act(self):
        pass


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
write_script = Writer('jane',scene="Bedtime stories")