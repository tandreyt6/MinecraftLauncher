import os
import sys
import requests
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication, QTextBrowser, QVBoxLayout, QWidget
from PyQt6.QtCore import QUrl
import webbrowser

minecraft_url = "https://www.minecraft.net"

class ArticleViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.lasthtml = None

        self.text_browser = QTextBrowser(self)
        self.text_browser.setOpenExternalLinks(True)

        self.text_browser.anchorClicked.connect(self.open_link)

        layout = QVBoxLayout()
        layout.addWidget(self.text_browser)
        self.setLayout(layout)

    def loadHtml(self, html="", css=""):
        if html:
            html = f"<meta name='viewport' content='width=device-width, initial-scale=1.0'>{html}"
            if css.strip() != "":
                html = f"<style>{css}</style>{html}"
            self.lasthtml = html
            self.text_browser.setHtml(html)

    def open_link(self, url: QUrl):
        if url.toString().startswith("http"):
            webbrowser.open(url.toString())
        else:
            webbrowser.open(minecraft_url+url.toString())
            self.text_browser.setHtml(self.lasthtml)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    example_article_data = {'url': '/ru-ru/article/minecraft-java-edition-1-21-3', 'image': 'https://www.minecraft.net/content/dam/minecraftnet/games/minecraft/screenshots/1.21.3%20277x277.jpg', 'header': 'Minecraft Java Edition 1.21.3', 'content_html': '<h1>Minecraft Java Edition 1.21.3</h1><div class="MC_Link_Style_RichText">\n<p>Coming in hot with a hotfix, here\'s Minecraft 1.21.3 with a fix for a critical issue affecting Realms with Resource Packs enabled.</p>\n<p>This version also fixes an upgrade problem with all Salmon turning small. This version will upgrade any small Salmon from previous versions into medium variants, including any from 1.21.2.</p>\n<p>Want to know about all the other changes in the Bundles of Bravery Drop? Check out the changelog <a href="/ru-ru/article/minecraft-java-edition-1-21-2">here</a>!</p>\n<h2>Fixed bugs in 1.21.3</h2>\n<ul>\n<li><a href="https://bugs.mojang.com/browse/MC-277791">MC-277791</a> - Attempting to join a Realm with a Resource Pack enabled fails with an error</li>\n<li><a href="https://bugs.mojang.com/browse/MC-277779">MC-277779</a> - Salmon from 1.21.1 or before shrink when updating to 1.21.2</li>\n</ul>\n<h2>Get the Release</h2>\n<p>To install the Release, open up the <a href="/content/minecraft-net/language-masters/download">Minecraft Launcher</a> and click play! Make sure your Launcher is set to the "Latest Release” option.</p>\n<p>Cross-platform server jar:</p>\n<ul>\n<li><a href="https://piston-data.mojang.com/v1/objects/45810d238246d90e811d896f87b14695b7fb6839/server.jar">Minecraft server jar</a></li>\n</ul>\n<p>Report bugs here:</p>\n<ul>\n<li><a href="https://bugs.mojang.com/projects/MC/summary">Minecraft issue tracker</a>!</li>\n</ul>\n<p>Want to give feedback?</p>\n<ul>\n<li>For any feedback and suggestions, head over to the <a href="https://feedback.minecraft.net/">Feedback site</a>. If you\'re feeling chatty, join us over at the <a href="https://discordapp.com/invite/minecraft">official Minecraft Discord</a>.</li>\n</ul>\n<p>\xa0</p>\n</div>'}

    font_id = QFontDatabase.addApplicationFont(
        "C:/Users/vovbo/Desktop/Tools_And_Assets/projects/python/MinecraftLauncher/UI/fonts/minecraftTen.ttf")
    if font_id == -1:
        sys.exit(-1)

    font_families = QFontDatabase.applicationFontFamilies(font_id)
    viewer = ArticleViewer()
    viewer.loadHtml(example_article_data['content_html'], """
    a { 
        color: #6CC349; 
    }
    
    p {
        font-size: 16px;
    }

    h1 { 
        font-family: '"""+font_families[0]+"""',"Noto Sans","Helvetica Neue","Helvetica","Arial","sans-serif";
    }
    
    h2 { 
        font-family: '"""+font_families[0]+"""',"Noto Sans","Helvetica Neue","Helvetica","Arial","sans-serif";
    }
""")
    viewer.setStyleSheet("background-color: #2C2F3A; color: #FCF5F1;")
    viewer.show()
    sys.exit(app.exec())
