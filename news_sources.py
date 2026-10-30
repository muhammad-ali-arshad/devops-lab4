from dataclasses import dataclass


@dataclass(frozen=True)
class NewsSource:
    name: str
    domains: tuple[str, ...]


SOURCES = (
    NewsSource("DAWN News Pakistan", ("dawn.com",)),
    NewsSource("ARY News Pakistan", ("arynews.tv",)),
    NewsSource("The News International Pakistan", ("thenews.com.pk",)),
    NewsSource("Pakistan Today", ("pakistantoday.com.pk",)),
    NewsSource("ProPakistani", ("propakistani.pk",)),
    NewsSource("TechJuice", ("techjuice.pk",)),
    NewsSource("The Nation Pakistan", ("nation.com.pk",)),
    NewsSource("Islamabad Post", ("islamabadpost.com.pk",)),
    NewsSource("Al Jazeera Media Network", ("aljazeera.com",)),
    NewsSource("NPR", ("npr.org",)),
    NewsSource("Deutsche Welle", ("dw.com",)),
    NewsSource("Euronews", ("euronews.com",)),
    NewsSource("NHK World Japan", ("www3.nhk.or.jp", "nhk.or.jp")),
    NewsSource("China Daily", ("chinadaily.com.cn",)),
    NewsSource("ABC News Australia", ("abc.net.au",)),
    NewsSource("Wired Magazine", ("wired.com",)),
    NewsSource("TechCrunch", ("techcrunch.com",)),
    NewsSource("Ars Technica", ("arstechnica.com",)),
    NewsSource("The Verge", ("theverge.com",)),
    NewsSource("MIT Technology Review", ("technologyreview.com",)),
)


def source_for(registration: str) -> NewsSource:
    if len(registration) < 3 or not registration[-3:].isdigit():
        raise ValueError("REGISTRATION must end in at least three digits")
    return SOURCES[(int(registration[-3:]) % 20)]
