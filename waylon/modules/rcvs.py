import logging
from collections import OrderedDict
import unicodecsv as csv
from dlcs.image_collection import Image, ImageCollection
from waylon.parser_output import Work
import settings


class Parser:

    def __init__(self, space=1):
        self.space = space

    def parse(self, original_filename, parse_file):

        logging.debug("parsing " + original_filename + " as " + parse_file)
        work = Work()
        toc = OrderedDict()
        flags = {}

        work.id = original_filename.rsplit('.', 1)[0][4:]

        with open(parse_file, 'rb') as csv_file:

            reader = csv.DictReader(
                csv_file,
                dialect='excel-tab',
                delimiter='\t',
                encoding='utf-8-sig'
            )
            images = []
            image_metadata = {}

            if original_filename.startswith('lib'):
                self.parse_library_data(reader, work, images, image_metadata, toc, flags)
            elif original_filename.startswith('arc'):
                self.parse_archive_data(reader, work, images, image_metadata, toc, flags)

            work.image_collection = ImageCollection(images)
            work.toc = toc
            work.image_metadata = image_metadata
            work.flags = flags

        return work

    def parse_archive_data(self, reader, work, images, image_metadata, toc, flags):

        first = True
        image_index = 0
        for row in reader:
            if first:
                work.label = row[ARC_WORK_TITLE_COLUMN]
                work.work_metadata = self.get_metadata_for_cols(row, ARC_WORK_COLS)
                viewing_mode = row[VIEWING_MODE_COLUMN]
                flags['Viewing_Mode'] = viewing_mode
                first = False
            else:

                origin = settings.RCVS_RELATIVE + row.get(ARC_FILENAME_COLUMN)
                image = Image(
                    space=settings.CURRENT_SPACE,
                    origin=origin,
                    string_1=work.id,
                    number_1=0,
                    number_2=image_index
                )
                images.append(image)

                # toc
                article_entries = map(lambda x: x.strip(), row.get(LIB_CONTENTS_COLUMN).split('|'))
                for article in article_entries:
                    if article not in toc:
                        toc[article] = []
                    toc[article].append(image_index)

                image_metadata[image_index] = self.get_metadata_for_cols(row, ARC_IMAGE_COLS)

                image_index += 1

    def parse_library_data(self, reader, work, images, image_metadata, toc, flags):

        first = True
        image_index = 0
        for row in reader:
            if first:
                work.label = row[LIB_WORK_TITLE_COLUMN]
                work.work_metadata = self.get_metadata_for_cols(row, LIB_WORK_COLS)
                viewing_mode = row[VIEWING_MODE_COLUMN]
                flags['Viewing_Mode'] = viewing_mode
                flags['Canvas_Label_Field'] = 'Page'
                first = False
            else:

                # images
                origin = settings.RCVS_RELATIVE + row.get(LIB_FILENAME_COLUMN)
                image = Image(
                    space=settings.CURRENT_SPACE,
                    origin=origin,
                    string_1=work.id,
                    number_1=0,
                    number_2=image_index
                )
                images.append(image)

                # toc
                article_entries = map(
                    lambda x: x.strip(),
                    row.get(LIB_CONTENTS_COLUMN, '').split('|')
                )
                for article in article_entries:
                    if article:
                        if article not in toc:
                            toc[article] = []
                        toc[article].append(image_index)

                # metadata
                image_metadata[image_index] = self.get_metadata_for_cols(row, LIB_IMAGE_COLS)
                image_index += 1

    def get_metadata_for_cols(self, row, cols):

        meta = []

        for column in cols:
            value = row.get(column)
            if value:
                meta.append({'label': column, 'value': value})

        return meta

    def custom_decoration(self, work, manifest):

        if work.flags:
            mode = work.flags.get('Viewing_Mode')
            if mode is not None and mode == "2":
                manifest['sequences'][0]['viewingHint'] = 'paged'


# --Column Mappings-- #

LIB_CONTENTS_COLUMN = 'Contents'
VIEWING_MODE_COLUMN = 'Viewing Mode'

# Library data columns names - work
LIB_FILENAME_COLUMN = 'File name'
LIB_WORK_TITLE_COLUMN = 'Work Title'
LIB_REPOSITORY_COLUMN = "Repository"
LIB_COLLECTION_COLUMN = 'Collection'
LIB_VOLUME_COLUMN = 'Volume'
LIB_CHAPTER_COLUMN = 'Chapter'
LIB_ISSUE_COLUMN = 'Issue'
LIB_DATE_COLUMN = 'Date'
LIB_PUBLICATION_INFO_COLUMN = 'Publication Info'
LIB_MATERIAL_TYPE_COLUMN = 'Material Type'
LIB_GENERAL_NOTE_COLUMN = 'General Note'
LIB_LANGUAGE_COLUMN = 'Language'
LIB_COPYRIGHT_COLUMN = 'Copyright'
LIB_PERMALINK_COLUMN = 'Permalink'


LIB_WORK_COLS = [
    LIB_WORK_TITLE_COLUMN,
    LIB_REPOSITORY_COLUMN,
    LIB_COLLECTION_COLUMN,
    LIB_VOLUME_COLUMN,
    LIB_CHAPTER_COLUMN,
    LIB_ISSUE_COLUMN,
    LIB_DATE_COLUMN,
    LIB_PUBLICATION_INFO_COLUMN,
    LIB_MATERIAL_TYPE_COLUMN,
    LIB_GENERAL_NOTE_COLUMN,
    LIB_LANGUAGE_COLUMN,
    LIB_COPYRIGHT_COLUMN,
    LIB_PERMALINK_COLUMN
]

# Library data columns names - image
LIB_PAGE_COLUMN = 'Page'
LIB_ARTICLE_COLUMN = 'Article'
LIB_AUTHOR_COLUMN = 'Author'
LIB_SUBJECT_COLUMN = 'Subject'
LIB_CATALOGUE_ENTRY_URL_COLUMN = 'Catalogue Entry URL'

LIB_IMAGE_COLS = [
    LIB_PAGE_COLUMN,
    LIB_ARTICLE_COLUMN,
    LIB_AUTHOR_COLUMN,
    LIB_SUBJECT_COLUMN,
    LIB_CATALOGUE_ENTRY_URL_COLUMN
]

# archive data column names - work
ARC_FILENAME_COLUMN = 'File name'
ARC_WORK_TITLE_COLUMN = 'Work Title'
ARC_REPOSITORY_COLUMN = 'Repository'
ARC_COLLECTION_COLUMN = 'Collection'
ARC_SERIES_COLUMN = 'Series'
ARC_SUB_SERIES_COLUMN = 'Subseries'
ARC_CATALOGUE_REF_COLUMN = 'Catalogue ref'
ARC_COPYRIGHT_COLUMN = 'Copyright'
ARC_PERMALINK_COLUMN = "Permalink"


ARC_WORK_COLS = [
    ARC_CATALOGUE_REF_COLUMN,
    ARC_WORK_TITLE_COLUMN,
    ARC_REPOSITORY_COLUMN,
    ARC_COLLECTION_COLUMN,
    ARC_SERIES_COLUMN,
    ARC_SUB_SERIES_COLUMN,
    ARC_COPYRIGHT_COLUMN,
    ARC_PERMALINK_COLUMN
]

# archive data column names - image
ARC_IMAGE_CATALOGUE_REF_COLUMN = 'Catalogue ref'
ARC_IMAGE_TITLE_COLUMN = 'Title'
ARC_DATE_COLUMN = 'Date'
ARC_DESCRIPTION_COLUMN = 'Description'
ARC_CREATOR_COLUMN = 'Creator'
ARC_FORMAT_COLUMN = 'Format'
ARC_CATALOGUE_ENTRY_URL_COLUMN = 'Catalogue Entry URL'

ARC_IMAGE_COLS = [
    ARC_CATALOGUE_REF_COLUMN,
    ARC_IMAGE_TITLE_COLUMN,
    ARC_DATE_COLUMN,
    ARC_DESCRIPTION_COLUMN,
    ARC_CREATOR_COLUMN,
    ARC_FORMAT_COLUMN,
    ARC_CATALOGUE_ENTRY_URL_COLUMN
]
