__author__ = 'ian'
from script import models
import json
import django

class SceneToJson:

    def __init__(self, scene):
        django.setup()
        self.scene = scene
        self.current_part = -1;
        self.scene_id = models.Scene.objects.get(title=scene).id
        self.json = {'meta': {'script': 'Jane',
                              'act': 'conversations'},
                     'scene': {'name': scene,
                               'parts': []}}
        self.process()
        self.print_to_file('mtl_complete')


    def process(self):
        scene = models.Scene.objects.get(title=self.scene).id
        for part_counter, part in enumerate(models.Part.objects.filter(scene_id=scene)):
            print('part count {0}'.format(part_counter))
            self.json['scene']['parts'].append({'name': part.name, 'content': []})

        for content_id in self.scene_content_ids():
            type = models.Type.objects.filter(content_id=content_id).first()
            print(type.name)
            self.branch(type.name, content_id)


    def scene_content_ids(self):
        scene = models.Scene.objects.get(title=self.scene).id
        for part in models.Part.objects.filter(scene_id=scene):
            for content in models.Content.objects.filter(part_id=part.id):
                yield content.id


    def branch(self, type_name, content_id, isChild=False):
        if type_name == 'SEQUENCE_SET':
            self.process_sequence_set(content_id)
        elif type_name == 'DEFAULT':
            self.process_default(content_id)
        elif type_name == 'ALTERNATIVE_FREE':
            self.process_alternative_free(content_id, isChild)
        elif type_name == 'ALTERNATIVE_COMPOUND':
            self.process_compound(content_id, isChild)
        elif type_name == 'ALTERNATIVE_PARENT':
            self.process_parent(content_id)
        elif type_name == 'ALTERNATIVE_PAIRED':
            self.process_paired(content_id)
        elif type_name == 'ALTERNATIVE_PAIRED_PARENT':
            self.process_paired_parent(content_id)
        elif type_name == 'ALTERNATIVE_PAIRED_MIXED':
            pass
        else:
            print('name not recognised in branch(): {0}'.format(type_name))

    def process_sequence_set(self, content_id):
        # since every sequence set in 'jane' starts a part - i.e. not portable with other projects!
        # Also set names are hardcoded here

        self.current_part += 1
        # if(self.current_part==1):
        #     print(json.dumps(self.json, indent=1))
        #     json_file = open('../json/mtl_f_expanded_2.json', 'w')
        #     json_file.write(json.dumps(self.json, indent=1))
        #     json_file.close()

        set_seq_content = {'id': content_id, 'type': 'SEQUENCE_SET', 'line': 'Pause', 'library': [], 'sets': [{'name': 'short', 'seqs':[]}, {'name':'medium', 'seqs': []}, {'name':'long', 'seqs': []}]}
        library_id = models.Group.objects.get(content_id=content_id, name='library').id
        sources = models.Group.objects.get(id=library_id).source.all()
        for source in sources:
            set_seq_content['library'].append({'id': source.id, 'duration': source.duration, 'file': source.file})

        #var setNames = ['short', 'medium', 'long']
        for set_counter, set_type in enumerate(['short', 'medium', 'long']):
            set_id = models.Group.objects.get(content_id=content_id, name=set_type).id
            seqs = models.GroupContainer.objects.filter(container_id=set_id)

            for seq_counter, seq in enumerate(seqs):
                sources = models.Group.objects.get(id=seq.group_id).source.all()
                seq_content=[]
                for source in sources:
                    seq_content.append({'file':source.file, 'duration': source.duration, 'id': source.id})

                set_seq_content['sets'][set_counter]['seqs'].append(seq_content)

        self.json['scene']['parts'][self.current_part]['content'].append(set_seq_content)
        print(json.dumps(self.json))


    def process_default(self, content_id, isChild=False, line_id=None):
        if isChild is False:
            line = models.Line.objects.get(content_id=content_id)
            sources = models.Line.objects.get(content_id=content_id).source.all()
        else:
            line = models.Line.objects.get(id=line_id)
            sources = models.Line.objects.get(id=line_id).source.all()

        default_content = []
        for source in sources:
            default_content.append({'file': source.file, 'duration': source.duration, 'id': source.id})

        default_content = {'id': content_id, 'line': line.line, 'line_id': line.id, 'speaker': line.speaker, 'type': 'DEFAULT', 'sources': default_content}
        print(json.dumps(default_content))

        if isChild is False:
            self.json['scene']['parts'][self.current_part]['content'].append(default_content)
        else:
            return default_content


    def process_alternative_free(self, content_id, isChild=False, group_id=None):
        alt_free_content = {'id': content_id, 'type': 'ALTERNATIVE_FREE', 'options': []}

        if isChild is False:
            alt_free_content = self.process_options(content_id, alt_free_content)
            self.json['scene']['parts'][self.current_part]['content'].append(alt_free_content)
            print(json.dumps(self.json, indent=1))
        else:
            alt_free_content = self.process_options(content_id, alt_free_content, isChild, group_id)
            return alt_free_content


    def process_options(self, content_id, alt_content, isChild=False, group_id=None):

        if isChild is False:
            if models.Type.objects.get(content_id=content_id).name != 'ALTERNATIVE_COMPOUND':
                lines = models.Group.objects.get(content_id=content_id).line.all()
            else:
                lines = models.Group.objects.get(content_id=content_id).line.all()[1:]
        else:

            if models.Type.objects.get(content_id=content_id, group_id=group_id).name != 'ALTERNATIVE_COMPOUND':
                lines = models.Group.objects.get(content_id=content_id, id=group_id).line.all()
            else:
                lines = models.Group.objects.get(content_id=content_id, id=group_id).line.all()[1:]

        for pos, line in enumerate(lines, start=1):
            option_content = {}
            print (line.line, pos)
            option_content['line'] = line.line
            option_content['speaker'] = line.speaker
            option_content['position'] = pos
            option_content['sources'] = []
            sources = models.Line.objects.get(id=line.id).source.all()
            for source in sources:
                print source.file
                option_content['sources'].append({'file': source.file, 'id': source.id, 'duration': source.duration})

            print(json.dumps(option_content))
            alt_content['options'].append(option_content)

        print(json.dumps(alt_content))
        print('=================')
        return alt_content


    def process_paired(self, content_id):
        args = models.Type.objects.get(content_id=content_id).arguments
        paired_content = {'id': content_id, 'type': 'ALTERNATIVE_PAIRED', 'options': [], 'arguments': json.loads(args)}
        paired_content = self.process_options(content_id, paired_content)
        self.json['scene']['parts'][self.current_part]['content'].append(paired_content)
        print(json.dumps(self.json, indent=1))


    def process_parent(self, content_id):
        parent_content = {'id': content_id, 'type': 'ALTERNATIVE_PARENT', 'children': []}
        group_id = models.Type.objects.get(content_id=content_id, name='ALTERNATIVE_PARENT').group_id
        children = models.GroupContainer.objects.filter(container_id=group_id)
        parent_content = self.process_children(content_id, children, parent_content)
        self.json['scene']['parts'][self.current_part]['content'].append(parent_content)
        self.print_to_file('mtl_up_to_parent')


    def process_paired_parent(self, content_id):
        args = models.Type.objects.get(content_id=content_id, name='ALTERNATIVE_PAIRED_PARENT').arguments
        paired_parent_content = {'id': content_id, 'type': 'ALTERNATIVE_PAIRED_PARENT', 'children': [], 'arguments': json.loads(args)}
        group_id = models.Type.objects.get(content_id=content_id, name='ALTERNATIVE_PAIRED_PARENT').group_id
        children = models.GroupContainer.objects.filter(container_id=group_id)
        paired_parent_content = self.process_children(content_id, children, paired_parent_content)
        self.json['scene']['parts'][self.current_part]['content'].append(paired_parent_content)
        self.print_to_file('mtl_up_to_paired_parent')


    def process_children(self, content_id, children, parent_content):
        for count, child in enumerate(children, start=1):
            print(child.group_id, models.Group.objects.get(id=child.group_id).name)
            child_type = models.Group.objects.get(id=child.group_id).name.upper()
            if(child_type == 'ALTERNATIVE_FREE'):
                child_content = self.process_alternative_free(content_id, True, child.group_id)
                child_content['position'] = count
                parent_content['children'].append(child_content)
                print(json.dumps(child_content))
            elif(child_type == 'ALTERNATIVE_COMPOUND'):
                child_content = self.process_compound(content_id, True, child.group_id)
                child_content['position'] = count
                parent_content['children'].append(child_content)
            else:
                print('child type for paired parent not recognized')

        return parent_content

    def process_compound(self, content_id, hasChild=False, group_id=None):
        compound_content = {'id': content_id, 'options': [], 'type': 'ALTERNATIVE_COMPOUND'}
        options = []

        if hasChild == False:
            lines = models.Group.objects.get(content_id=content_id).line.all()
        else:
            lines = models.Group.objects.get(content_id=content_id, id=group_id).line.all()

        default_content = self.process_default(content_id, True, lines[0].id)
        print(lines[0].id)
        compound_content['default'] = default_content
        compound_content = self.process_options(content_id, compound_content, True, group_id)

        if hasChild == True:
            return compound_content
            pass

    def print_to_file(self, filename):
        json_file = open('../json/{0}.json'.format(filename), 'w')
        json_file.write(json.dumps(self.json, indent=1))
        json_file.close()
        pass

jsonScene = SceneToJson('marriedtoolong')