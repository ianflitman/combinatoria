
class PartBox(object):

    def __init__(self, part_id):
        self.id = part_id
        self.contents = [ContentBox]

    def __iter__(self):
        return self.iter()

    def iter(self, id):
        return self.match(iter(self.contents), id)

    def match(self, iter, id):
        for content in self.contents:
            if content.id == id:
                return content
            pass


    def next(self):
        pass

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
            print(yield)
            #if content.id == content_id:
        #     return content

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


contentBoxes = []

contentBoxes.append(ContentBox(5))
contentBoxes.append(ContentBox(15))
contentBoxes.append(ContentBox(22))
contentBoxes.append(ContentBox(50))

partBox = PartBox(1)
partBox.contents = contentBoxes


def searchBoxes(id):
    partBox.get_content(id)


searchBoxes(20)


