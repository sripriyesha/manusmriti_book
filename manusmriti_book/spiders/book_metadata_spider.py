from pathlib import Path
import json
import sys

import scrapy
from scrapy.http import Request


class BookMetadataSpider(scrapy.Spider):
    name = "book_metadata"

    # start_urls = [
    #     "https://www.wisdomlib.org/hinduism/book/manusmriti-with-the-commentary-of-medhatithi/d/doc145369.html",
    #     "https://www.wisdomlib.org/hinduism/book/manusmriti-with-the-commentary-of-medhatithi/d/doc145570.html",
    #     "https://www.wisdomlib.org/hinduism/book/manusmriti-with-the-commentary-of-medhatithi/d/doc199769.html",
    #     "https://www.wisdomlib.org/hinduism/book/manusmriti-with-the-commentary-of-medhatithi/d/doc200093.html",
    #     "https://www.wisdomlib.org/hinduism/book/manusmriti-with-the-commentary-of-medhatithi/d/doc200373.html",
    #     "https://www.wisdomlib.org/hinduism/book/manusmriti-with-the-commentary-of-medhatithi/d/doc200554.html",
    #     "https://www.wisdomlib.org/hinduism/book/manusmriti-with-the-commentary-of-medhatithi/d/doc200659.html",
    #     "https://www.wisdomlib.org/hinduism/book/manusmriti-with-the-commentary-of-medhatithi/d/doc200893.html",
    #     "https://www.wisdomlib.org/hinduism/book/manusmriti-with-the-commentary-of-medhatithi/d/doc201357.html",
    #     "https://www.wisdomlib.org/hinduism/book/manusmriti-with-the-commentary-of-medhatithi/d/doc201731.html",
    #     "https://www.wisdomlib.org/hinduism/book/manusmriti-with-the-commentary-of-medhatithi/d/doc201875.html",
    #     "https://www.wisdomlib.org/hinduism/book/manusmriti-with-the-commentary-of-medhatithi/d/doc202173.html",
    # ]

    def __init__(self, *args, **kwargs):
        super(BookMetadataSpider, self).__init__(*args, **kwargs)

        with open("subheading_heading_map.json") as f:
            self.subheading_heading_map = json.load(f)
            f.close()

        with open("verses_links.txt") as f:
            self.start_urls = [url.strip() for url in f.readlines()]

        # self.start_urls = [
        #     # 1.1
        #     # "https://www.wisdomlib.org/hinduism/book/manusmriti-with-the-commentary-of-medhatithi/d/doc145371.html"
        #     # 1.14-15
        #     "https://www.wisdomlib.org/hinduism/book/manusmriti-with-the-commentary-of-medhatithi/d/doc145413.html"
        #     # 1.28-29
        #     # "https://www.wisdomlib.org/hinduism/book/manusmriti-with-the-commentary-of-medhatithi/d/doc145433.html"
        # ]

    def parse(self, response):
        def replace_html_tags(str):
            return (
                str.replace("<em>", "")
                .replace("</em>", "")
                .replace("<p>", "")
                .replace('<p style="text-align: center;">', "")
                .replace("</p>", "")
                .replace("<br>", "")
                .replace("<strong>", "")
                .replace("</strong>", "")
            )

        # links = response.xpath("//a[contains(text(), 'Verse')]//@href").getall()

        # with open("links.txt", "a") as f:
        #     for link in links:
        #         f.write(response.urljoin(link) + "\n")

        section = response.xpath(
            "//nav[contains(text(), 'parent:')]//following-sibling::span[1]//following-sibling::a[1]/descendant-or-self::node()//text()"
        ).get()
        discourse = self.subheading_heading_map[section]
        verse_number = (
            response.xpath("//h1[contains(@class, 'h2')]//text()")
            .get()
            .split("[")[0]
            .strip()
        )
        print(verse_number)

        blockquotes = response.xpath("//blockquote")

        if len(blockquotes) == 1:
            sanskrit_verse = replace_html_tags(
                response.xpath("//blockquote//p[2]").get()
            )
            unicode_transliteration = replace_html_tags(response.xpath(".//p[3]").get())
            english_translation = replace_html_tags(
                response.xpath("//blockquote//p[4]").get()
            )
            commentary = replace_html_tags(
                "".join(
                    response.xpath(
                        "//blockquote//following-sibling::h2[contains(text(), 'commentary')]//following-sibling::p[following-sibling::h2]"
                    ).getall()
                )
            )
            explanatory_notes = replace_html_tags(
                "".join(
                    response.xpath(
                        "//blockquote//following-sibling::h2[contains(text(), 'Explanatory notes')]//following-sibling::p"
                    ).getall()
                )
            )
            comparative_notes = ""

            yield {
                "discourse": discourse,
                "section": section,
                "verse_number": verse_number,
                "sanskrit_verse": sanskrit_verse,
                "unicode_transliteration": unicode_transliteration,
                "english_translation": english_translation,
                "commentary": commentary,
                "explanatory_notes": explanatory_notes,
                "comparative_notes": comparative_notes,
            }
        else:
            for blockquote in blockquotes:
                sanskrit_verse = replace_html_tags(blockquote.xpath(".//p[2]").get())
                unicode_transliteration = replace_html_tags(
                    blockquote.xpath(".//p[3]").get()
                )
                english_translation = replace_html_tags(
                    blockquote.xpath(".//p[4]").get()
                )
                commentary = replace_html_tags(
                    "".join(
                        blockquote.xpath(
                            ".//following-sibling::h2[contains(text(), 'commentary')]//following-sibling::p[following-sibling::h2 or following-sibling::blockquote]"
                        ).getall()
                    )
                )
                comparative_notes = replace_html_tags(
                    "".join(
                        blockquote.xpath(
                            ".//following-sibling::h2[3 and contains(text(), 'Comparative notes')]//following-sibling::p"
                        ).getall()
                    )
                )

                if comparative_notes != "":
                    explanatory_notes = replace_html_tags(
                        "".join(
                            blockquote.xpath(
                                ".//following-sibling::h2[2 and contains(text(), 'Explanatory notes')]//following-sibling::p[following-sibling::h2]"
                            ).getall()
                        )
                    )
                else:
                    explanatory_notes = replace_html_tags(
                        "".join(
                            blockquote.xpath(
                                ".//following-sibling::h2[2 and contains(text(), 'Explanatory notes')]//following-sibling::p"
                            ).getall()
                        )
                    )

                yield {
                    "discourse": discourse,
                    "section": section,
                    "verse_number": verse_number,
                    "sanskrit_verse": sanskrit_verse,
                    "unicode_transliteration": unicode_transliteration,
                    "english_translation": english_translation,
                    "commentary": commentary,
                    "explanatory_notes": explanatory_notes,
                    "comparative_notes": comparative_notes,
                }

    def get_subheadings(self, response, heading_text):
        subheadings_texts = self.get_headings_texts(response, "+")
        subheadings_links = self.get_headings_links(response, "+")
        subheading_heading_map = {}

        i = 0
        while i < len(subheadings_texts):
            subheading_text = subheadings_texts[i]
            subheading_link = subheadings_links[i]

            subheading_heading_map[subheading_text] = heading_text

            i = i + 1

        yield subheading_heading_map

    def get_verses_titles_links(self, response, heading_text, subheading_text):
        def get_verses_titles():
            return response.xpath(
                "//a[contains(text(), 'Verse')]" + "//text()"
            ).getall()

        def get_verses_links():
            return response.xpath(
                "//span[contains(@class, 'il-sign')]"
                + "//following-sibling::a"
                + "//@href"
            ).getall()

        verses_titles = get_verses_titles()
        verses_links = get_verses_links()

        i = 0
        while i < len(verses_titles):
            verse_title = verses_titles[i]
            verse_link = verses_links[i]

            yield Request(
                response.urljoin(verse_link),
                callback=self.get_verse,
                cb_kwargs=dict(
                    heading_text=heading_text,
                    subheading_text=subheading_text,
                    verse_title=verse_title,
                ),
                dont_filter=True,
            )

            i = i + 1

    def get_verse(self, response, heading_text, subheading_text, verse_title):
        print_dict = {
            "heading_text": heading_text.split("-")[0],
            "subheading_text": subheading_text.split("-")[0],
            "verse_title": verse_title,
        }
        print("{heading_text}/{subheading_text}/{verse_title}".format(**print_dict))

    def save_file(self, response, filename):
        Path(f"./books/page_{self.page}/").mkdir(parents=True, exist_ok=True)

        path = f"./books/page_{self.page}/{filename}"
        self.logger.info("Saving file %s", path)
        with open(path, "wb") as f:
            f.write(response.body)

    def get_headings_texts(self, response, key):
        return response.xpath(
            "//span[contains(text(), '"
            + key
            + "')]"
            + "/following-sibling::a"
            + "//text()"
        ).getall()

    def get_headings_links(self, response, key):
        return response.xpath(
            "//span[contains(text(), '"
            + key
            + "')]"
            + "/following-sibling::a"
            + "//@href"
        ).getall()
