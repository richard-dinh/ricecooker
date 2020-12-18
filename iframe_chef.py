
from ricecooker.chefs import SushiChef
from ricecooker.classes.nodes import ChannelNode, TopicNode, VideoNode, HTML5AppNode
from ricecooker.classes import nodes, files, licenses
from ricecooker.classes.licenses import get_license
from ricecooker.utils.youtube import YouTubeVideoUtils
from ricecooker.utils.downloader import archive_page, read
from ricecooker.utils.zip import create_predictable_zip
from ricecooker.classes.licenses import CC_BYLicense
import glob
import os
import shutil
from bs4 import BeautifulSoup
import sys
class SimpleChef(SushiChef):
    channel_info = {
        "CHANNEL_TITLE": "HTML5 practice channel",
        "CHANNEL_SOURCE_DOMAIN": "richard@dinh.com",  # where content comes from
        "CHANNEL_SOURCE_ID": "HTML5_app_practice",  # CHANGE ME!!!
        "CHANNEL_LANGUAGE": "en",  # le_utils language code
        "CHANNEL_THUMBNAIL": "https://upload.wikimedia.org/wikipedia/commons/b/b7/A_Grande_Batata.jpg",  # (optional)
        "CHANNEL_DESCRIPTION": "What is this channel about?",  # (optional)
    }

    def construct_channel(self, **kwargs):
        channel = self.get_channel(**kwargs)

        topic_node = TopicNode(
            title = 'HTML5 practice topic Node',
            source_id = 'richard_HTML5_practice_source_id',
            author = 'Richard',
            provider = 'Richard',
            description = 'HTML5 practice',
            language = 'en'
        )

        os.makedirs(os.path.join('chefdata', 'tempfiles'), exist_ok = True)
        
        HTML5_FOLDER = os.path.join('chefdata', 'HTML5')
        TEMPFILES_FOLDER = os.path.join('chefdata', 'tempfiles')

        # html5_url = 'https://bibliotheque.sesamath.net/public/voir/5c5d6e0d830f3437fdd1119d?inc=25&resultatMessageAction=saveResultat'
        html5_url = 'https://bibliotheque.sesamath.net/public/voir/5f76033e7166a20ae7ae8e2b?inc=102&resultatMessageAction=saveResultat'

        page = archive_page(html5_url, HTML5_FOLDER)
        # ENTRY FOR CREATE_PREDICTABLE_ZIP BELOW
        entry = page['index_path']
        index_path = os.path.join(HTML5_FOLDER, 'index.html')
        shutil.copy(entry, index_path)
        # Updating path to be relative to zip file
        # zip_path_entry = os.path.relpath(entry, 'chefdata\\HTML5')


        js_files = glob.iglob('**/*.js', recursive=True)
        for afile in js_files:
            # The JS files can contain absolute links in code, so we need to 
            # replace them.
            content =  open(afile, encoding= 'utf-8').read()
            content = content.replace('https://', '')
            content = content.replace('https?:\/\/', '')
            content = content.replace('/^(https?:)?\/\//.test(e)&&', '')
            content = content.replace('//j3p.sesamath', 'j3p.sesamath')
            assert not 'https://' in content
            with open(afile, 'w', encoding= 'utf-8') as f:
                f.write(content)

        zippath = create_predictable_zip(HTML5_FOLDER)

        # zippath = create_predictable_zip(SESAMATH_FOLDER)
        # zippath = create_predictable_zip(SAMPLE_FOLDER)
        shutil.copy(zippath, TEMPFILES_FOLDER)
        htmlNode = nodes.HTML5AppNode(
            source_id = 'HTML5_sample',
            files = [files.HTMLZipFile(zippath)],
            title = 'HTML5 Sample',
            description = 'sample',
            license= CC_BYLicense("Learning Equality"),
            language = 'en',
            thumbnail = None,
            author = 'Learning Equality'
        )


        topic_node.add_child(htmlNode)
        channel.add_child(htmlNode)
        # for child in channel.children:
        #     for content_file in child.files:
        #         print(content_file)

        return channel


settings = {
    'generate-missing-thumbnails': False,
    'compress-videos': False
}

if __name__ == "__main__":
    """
    Run this script on the command line using:
        python sushichef.py  --token=YOURTOKENHERE9139139f3a23232
    """
    # simple_chef = SimpleChef()
    # simple_chef.main()
    # content = read('{0}'.format('https://mathenpoche.sesamath.net/?page=sixieme#sixieme_1_5_1_sesabibli/5f76033e7166a20ae7ae8e2b', loadjs=True))
    # print(content)
    # content = read('{0}'.format('https://mathenpoche.sesamath.net/?page=sixieme#sixieme_1_5_1_sesabibli/5f7603d67166a20ae7ae8e2c', loadjs=True))
    # print(content)
    try:
        content = read('https://mathenpoche.sesamath.net/?page=sixieme#sixieme_1_5_1', loadjs = True)
    except: 
        print('Timeout Error')
    iframes = []
    page_soup = BeautifulSoup(content[0], 'html.parser')

    visible_ress_ato = page_soup.find_all('a', {'class' : 'ress_ato'})
    visible_ress_j3p = page_soup.find_all('a', {'class' : 'ress_j3p'})

    for element in visible_ress_ato:
        # if timeout error, attempt to connect 10 times before continuing
        attemps = 0
        while attemps in range(10):
            try:
                print('calling read function on {0}{1}'.format('https://mathenpoche.sesamath.net/?page=sixieme', element['href']))
                content = read('{0}{1}'.format('https://mathenpoche.sesamath.net/?page=sixieme', element['href']), loadjs=True)
            except:
                print('Error getting iframe at {0}'.format(element['href']))
                print('Failed attempt number: {0}'.format(attemps))
                attemps+=1
                continue
            break
        # Continue to next item if attemps greater than 10
        if attemps >= 10:
            continue
        iframe_soup = BeautifulSoup(content[0], 'html.parser')
        visible_iframe = iframe_soup.find('iframe')
        source = visible_iframe['src']
        print(source)
        iframes.append(source)
        
    for element in visible_ress_j3p:
        # if timeout error, attempt to connect 10 times before continuing
        attemps = 0
        while attemps in range(10):
            try:
                print('calling read function on {0}{1}'.format('https://mathenpoche.sesamath.net/?page=sixieme', element['href']))
                content = read('{0}{1}'.format('https://mathenpoche.sesamath.net/?page=sixieme', element['href']), loadjs=True)
            except:
                print('Error getting iframe at {0}'.format(element['href']))
                print('Failed attempt number: {0}'.format(attemps))
                attemps+=1
                continue
            break
        # Continue to next item if attemps greater than 10
        if attemps >= 10:
            continue
        iframe_soup = BeautifulSoup(content[0], 'html.parser')
        visible_iframe = iframe_soup.find('iframe')
        source = visible_iframe['src']
        iframes.append(source)
        print(source)
    print(iframes)