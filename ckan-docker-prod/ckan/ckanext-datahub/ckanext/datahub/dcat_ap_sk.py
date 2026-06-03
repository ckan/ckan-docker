import os
from urllib.parse import urlparse

from ckanext.dcat.profiles import RDFProfile
from rdflib import BNode, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, FOAF, RDF


DCAT = Namespace("http://www.w3.org/ns/dcat#")
LEG = Namespace("https://data.gov.sk/def/ontology/legislation/")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")


DEFAULTS = {
    "DATAHUB_DCAT_PUBLISHER_URI": "https://data.gov.sk/id/legal-subject/00164381",
    "DATAHUB_DCAT_PUBLISHER_NAME": (
        "Ministerstvo školstva, výskumu, vývoja a mládeže Slovenskej republiky"
    ),
    "DATAHUB_DCAT_CONTACT_NAME": "DataHub Open Data",
    "DATAHUB_DCAT_CONTACT_EMAIL": "opendata@example.gov.sk",
    "DATAHUB_DCAT_DEFAULT_FORMAT_URI": (
        "http://publications.europa.eu/resource/authority/file-type/CSV"
    ),
    "DATAHUB_DCAT_DEFAULT_MEDIA_TYPE_URI": (
        "http://www.iana.org/assignments/media-types/text/csv"
    ),
    "DATAHUB_DCAT_TERMS_AUTHORS_WORK_TYPE": (
        "https://data.gov.sk/def/authors-work-type/3"
    ),
    "DATAHUB_DCAT_TERMS_ORIGINAL_DATABASE_TYPE": (
        "https://data.gov.sk/def/original-database-type/3"
    ),
    "DATAHUB_DCAT_TERMS_DATABASE_PROTECTED_BY_SPECIAL_RIGHTS_TYPE": (
        "https://data.gov.sk/def/codelist/database-creator-special-rights-type/2"
    ),
    "DATAHUB_DCAT_TERMS_PERSONAL_DATA_CONTAINMENT_TYPE": (
        "https://data.gov.sk/def/personal-data-occurence-type/2"
    ),
}


class DataHubDCATAPSKProfile(RDFProfile):
    def parse_dataset(self, dataset_dict, dataset_ref):
        return dataset_dict

    def graph_from_catalog(self, catalog_dict, catalog_ref):
        self._bind_namespaces()
        self._normalize_publisher(catalog_ref)

    def graph_from_dataset(self, dataset_dict, dataset_ref):
        self._bind_namespaces()
        self._normalize_publisher(dataset_ref)
        self._ensure_keywords(dataset_dict, dataset_ref)
        self._ensure_contact_point(dataset_ref)

        distributions = set(self.g.objects(dataset_ref, DCAT.distribution))
        distributions.update(self.g.subjects(RDF.type, DCAT.Distribution))
        for distribution in distributions:
            self._normalize_distribution(distribution)

    def _setting(self, key):
        return os.environ.get(key, DEFAULTS[key])

    def _publisher(self):
        return URIRef(self._setting("DATAHUB_DCAT_PUBLISHER_URI"))

    def _bind_namespaces(self):
        self.g.bind("leg", LEG)

    def _normalize_publisher(self, subject):
        publisher = self._publisher()
        self.g.remove((subject, DCTERMS.publisher, None))
        self.g.add((subject, DCTERMS.publisher, publisher))

        self.g.add((publisher, RDF.type, FOAF.Agent))
        self.g.remove((publisher, FOAF.name, None))
        self.g.add(
            (
                publisher,
                FOAF.name,
                Literal(self._setting("DATAHUB_DCAT_PUBLISHER_NAME")),
            )
        )

    def _ensure_keywords(self, dataset_dict, dataset_ref):
        if list(self.g.objects(dataset_ref, DCAT.keyword)):
            return

        keywords = []
        for tag in dataset_dict.get("tags") or []:
            keyword = tag.get("display_name") or tag.get("name")
            if keyword:
                keywords.append(keyword)

        if not keywords and dataset_dict.get("tag_string"):
            keywords.extend(
                keyword.strip()
                for keyword in dataset_dict["tag_string"].split(",")
                if keyword.strip()
            )

        if not keywords:
            fallback = dataset_dict.get("title") or dataset_dict.get("name")
            if fallback:
                keywords.append(fallback)

        for keyword in keywords:
            self.g.add((dataset_ref, DCAT.keyword, Literal(keyword)))

    def _ensure_contact_point(self, dataset_ref):
        if list(self.g.objects(dataset_ref, DCAT.contactPoint)):
            return

        contact_name = self._setting("DATAHUB_DCAT_CONTACT_NAME")
        contact_email = self._setting("DATAHUB_DCAT_CONTACT_EMAIL")
        if not contact_name and not contact_email:
            return

        contact = BNode()
        self.g.add((dataset_ref, DCAT.contactPoint, contact))
        self.g.add((contact, RDF.type, VCARD.Kind))
        if contact_name:
            self.g.add((contact, VCARD.fn, Literal(contact_name)))
        if contact_email:
            self.g.add((contact, VCARD.hasEmail, URIRef(f"mailto:{contact_email}")))

    def _normalize_distribution(self, distribution):
        access_urls = list(self.g.objects(distribution, DCAT.accessURL))
        if access_urls and not list(self.g.objects(distribution, DCAT.downloadURL)):
            for access_url in access_urls:
                self.g.add((distribution, DCAT.downloadURL, access_url))

        if self._is_csv_distribution(distribution):
            self.g.remove((distribution, DCTERMS.format, None))
            self.g.add(
                (
                    distribution,
                    DCTERMS.format,
                    URIRef(self._setting("DATAHUB_DCAT_DEFAULT_FORMAT_URI")),
                )
            )

            self.g.remove((distribution, DCAT.mediaType, None))
            self.g.add(
                (
                    distribution,
                    DCAT.mediaType,
                    URIRef(self._setting("DATAHUB_DCAT_DEFAULT_MEDIA_TYPE_URI")),
                )
            )

        self._replace_terms_of_use(distribution)

    def _replace_terms_of_use(self, distribution):
        for terms_of_use in list(self.g.objects(distribution, LEG.termsOfUse)):
            self.g.remove((distribution, LEG.termsOfUse, terms_of_use))
            self.g.remove((terms_of_use, None, None))

        terms_of_use = BNode()
        self.g.add((distribution, LEG.termsOfUse, terms_of_use))
        self.g.add((terms_of_use, RDF.type, LEG.TermsOfUse))
        self.g.add(
            (
                terms_of_use,
                LEG.authorsWorkType,
                URIRef(self._setting("DATAHUB_DCAT_TERMS_AUTHORS_WORK_TYPE")),
            )
        )
        self.g.add(
            (
                terms_of_use,
                LEG.originalDatabaseType,
                URIRef(self._setting("DATAHUB_DCAT_TERMS_ORIGINAL_DATABASE_TYPE")),
            )
        )
        self.g.add(
            (
                terms_of_use,
                LEG.databaseProtectedBySpecialRightsType,
                URIRef(
                    self._setting(
                        "DATAHUB_DCAT_TERMS_DATABASE_PROTECTED_BY_SPECIAL_RIGHTS_TYPE"
                    )
                ),
            )
        )
        self.g.add(
            (
                terms_of_use,
                LEG.personalDataContainmentType,
                URIRef(
                    self._setting(
                        "DATAHUB_DCAT_TERMS_PERSONAL_DATA_CONTAINMENT_TYPE"
                    )
                ),
            )
        )

    def _is_csv_distribution(self, distribution):
        values = []
        for predicate in (
            DCTERMS.format,
            DCAT.mediaType,
            DCAT.accessURL,
            DCAT.downloadURL,
        ):
            values.extend(self.g.objects(distribution, predicate))

        return any(self._is_csv_value(value) for value in values)

    def _is_csv_value(self, value):
        value_text = str(value).strip().lower()
        if value_text in {
            "csv",
            "text/csv",
            self._setting("DATAHUB_DCAT_DEFAULT_FORMAT_URI").lower(),
            self._setting("DATAHUB_DCAT_DEFAULT_MEDIA_TYPE_URI").lower(),
            DEFAULTS["DATAHUB_DCAT_DEFAULT_FORMAT_URI"].lower(),
            DEFAULTS["DATAHUB_DCAT_DEFAULT_MEDIA_TYPE_URI"].lower(),
        }:
            return True

        parsed = urlparse(value_text)
        path = parsed.path.rstrip("/")
        return path.endswith(".csv")
