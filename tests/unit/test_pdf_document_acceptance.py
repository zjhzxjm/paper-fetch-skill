"""Real wrong-document/preview and synthetic supplement rejection regressions."""

import pytest
from paper_fetch.providers import _pdf_common, _pdf_candidates
from paper_fetch.providers._pdf_document import non_article_pdf_reason
from tests.support._paper_fetch_support import build_pdf_bytes


PREFIX = "acquisition/subscription-2026-09-15/"
BAD_DOWNLOADS = [
    (
        "10.1063/5.0260731",
        "https://vergil.chemistry.gatech.edu/static/content/ci.pdf",
        "pdf_identity_unverified",
    ),
    (
        "10.1175/jas-d-26-0015.1",
        "https://journals.ametsoc.org/previewpdf/view/journals/atsc/83/9/JAS-D-26-0015.1.xml",
        "pdf_preview_only",
    ),
]


@pytest.mark.parametrize(
    "url",
    [
        "https://pubs.acs.org/jafcau/article-supplement/3643102/pdf/jf5c06949_si_001/",
        "https://onlinelibrary.wiley.com/doi/suppl/10.1002/ptr.8472/supinfo/ptr8472-sup-0001.pdf",
        "https://example.org/jf5c06949_si_001.pdf",
        "https://example.org/ptr8472-sup-0001.pdf",
    ],
)
def test_publisher_supplement_paths_are_excluded_without_label_evidence(url):
    assert non_article_pdf_reason(url) == "pdf_supplement_only"
    assert _pdf_candidates.extract_pdf_candidate_urls_from_html(
        f'<a href="{url}">PDF</a><a href="/article.pdf">Full text PDF</a>',
        "https://example.org/article",
    ) == ["https://example.org/article.pdf"]
    with pytest.raises(_pdf_common.PdfFetchFailure) as error:
        _pdf_common.pdf_fetch_result_from_bytes(
            artifact_dir=None,
            source_url="https://example.org/download",
            final_url=url,
            pdf_bytes=b"%PDF-1.7",
            allow_pdf_only=True,
        )
    assert error.value.kind == "pdf_supplement_only"


@pytest.mark.parametrize(
    "url",
    [
        "https://pubs.acs.org/doi/pdf/10.1021/acs.jafc.5c06949",
        "https://onlinelibrary.wiley.com/doi/pdf/10.1002/ptr.8472",
    ],
)
def test_main_pdf_paths_remain_candidates(url):
    assert non_article_pdf_reason(url) is None


def test_supplement_cannot_hide_behind_generic_download_url():
    # Synthetic role evidence; the real supplementary payload was removed.
    with pytest.raises(_pdf_common.PdfFetchFailure, match="supplementary"):
        _pdf_common.pdf_fetch_result_from_bytes(
            artifact_dir=None,
            source_url="https://example.org/download",
            final_url="https://example.org/download",
            pdf_bytes=build_pdf_bytes(
                ["Supplementary Information", "Supplementary methods and data"]
            ),
            allow_pdf_only=True,
        )
