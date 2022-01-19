from django import template

from hyphaeTaxonomy.models import HigherRankTaxon, Name

register = template.Library()


@register.filter
def full_rank(value):
    return HigherRankTaxon.RANKS[value]


@register.filter
def name_citation(value):
    y_on_pub_txt = f" [{value.year_on_publication}]" if value.year_on_publication is not None else ""
    vol_txt = f" {value.volume}" if value.volume is not None else ""
    part_txt = f"({value.part})" if value.part is not None else ""
    icn_id_txt = f" [#{value.icn_identifier}]" if value.icn_identifier is not None else ""
    return f"<i>{value.name}</i> {value.authors} ({value.year_of_publication}){y_on_pub_txt}, {value.literature}{vol_txt}{part_txt}: {value.page}{icn_id_txt}"
