from src.bean.cve_info import CVEInfo
from src.crawler.base import BaseCrawler
from src.utils import log
import httpx
import json
import re


class QiAnXin(BaseCrawler):
    name_ch = "奇安信"
    name_en = "QiAnXin"
    home_page = "https://ti.qianxin.com/advisory/"
    url = "https://ti.qianxin.com/advisory/"

    def get_cves(self):
        response = httpx.get(self.url, headers=self.headers, timeout=self.timeout)

        cves = []
        if response.status_code == 200:
            html = response.content.decode("utf8")
            titles = self.get_titles(html)
            json_obj = json.loads(self.to_json(html))

            idx = 0
            for obj in json_obj.get("msg"):
                cve = self.to_cve(obj, titles[idx])
                idx += 1
                if cve.is_vaild():
                    cves.append(cve)
                    # log.debug(cve)
        else:
            log.warn(
                "获取 [%s] 威胁情报失败： [HTTP Error %i]" % (self.name_ch, response.status_code)
            )
        return cves

    def get_titles(self, html):
        titles = re.findall(
            r'<a tag="div" target="_blank" data-v-4e3604fb>(.*?)<!---->',
            html,
            re.DOTALL,
        )
        return titles

    def to_json(self, html):
        json_str = '{ "msg": [] }'
        rst = re.findall(r"(\{success:e,msg:.*?\],pageTotal)", html, re.DOTALL)
        if rst:
            json_str = rst[0]
            json_str = json_str.replace('"', "")
            json_str = json_str.replace(",pageTotal", "}")
            json_str = re.sub(r"success:[\w\$]+,", "", json_str)
            json_str = re.sub(r"_id:[\w\$]+,", "", json_str)
            json_str = re.sub(r"title:[\w\$]+,", "", json_str)
            json_str = re.sub(r"category:[\w\$]+,", "", json_str)
            json_str = re.sub(r"isPdfArticle:[\w\$]+,", "", json_str)
            json_str = re.sub(r"isAdvisorArticle:[\w\$]+,", "", json_str)
            json_str = re.sub(r"author:[\w\$]+,", "", json_str)
            json_str = re.sub(r"headImg:[\w\$]+,", "", json_str)
            json_str = re.sub(r"descImg:[\w\$]+,", "", json_str)
            json_str = re.sub(r"pdfFile:[\w\$]+,", "", json_str)
            json_str = re.sub(r"iocFile:[\w\$]+,", "", json_str)
            json_str = re.sub(r"campaign:[\w\$]+,", "", json_str)
            json_str = re.sub(r"degree:[\w\$]+,", "", json_str)
            json_str = re.sub(r"area:\[.*?\],", "", json_str)
            json_str = re.sub(r"industries:\[.*?\],", "", json_str)
            json_str = re.sub(r"aggressor_type:\[.*?\],", "", json_str)
            json_str = json_str.replace("msg:", '"msg":')
            json_str = json_str.replace("readableId:", '"readableId":"')
            json_str = json_str.replace(",content:", '","content":"')
            json_str = json_str.replace(",abstract:", '","abstract":"')
            json_str = json_str.replace(",tags:", '","tags":"')
            json_str = json_str.replace(",publish_time:", '","publish_time":"')
            json_str = json_str.replace(",permlink:", '","permlink":"')
            json_str = json_str.replace("}", '"}')
            json_str = json_str.replace(']"}', "]}")
        return json_str

    def to_cve(self, json_obj, title):
        cve = CVEInfo()
        cve.src = self.name_ch
        cve.url = json_obj.get("permlink") or ""
        cve.info = (json_obj.get("abstract") or "").strip().replace("\n\n", "\n")
        cve.title = title.strip()

        utc_time = json_obj.get("publish_time") or ""  # utc_time to datetime
        cve.time = utc_time.replace("T", " ").replace(".000Z", "")

        content = json_obj.get("content")
        rst = re.findall(r"ID(</strong>)?</td>\n<td>(.*?)</td>", content)
        if rst:
            if "<br>" in rst[0][1]:
                ids = rst[0][1].split("<br>")
            else:
                ids = rst[0][1].split(" ")
            cve.id = ", ".join(ids)
        return cve


if __name__ == "__main__":
    print(QiAnXin().get_cves())
