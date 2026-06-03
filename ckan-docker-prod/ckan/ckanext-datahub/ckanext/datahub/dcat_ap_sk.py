import os
from urllib.parse import urlparse

import ckan.plugins.toolkit as toolkit
from ckanext.dcat.profiles import RDFProfile
from rdflib import BNode, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, FOAF, RDF


DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCATAP = Namespace("http://data.europa.eu/r5r/")
FILETYPE = Namespace("http://publications.europa.eu/resource/authority/file-type/")
FREQ = Namespace("http://publications.europa.eu/resource/authority/frequency/")
LANGUAGE = Namespace("http://publications.europa.eu/resource/authority/language/")
LEG = Namespace("https://data.gov.sk/def/ontology/legislation/")
TEXT = Namespace("http://www.iana.org/assignments/media-types/text/")
THEME = Namespace("http://publications.europa.eu/resource/authority/data-theme/")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")


DEFAULTS = {
    "DATAHUB_DCAT_PUBLISHER_URI": "https://data.gov.sk/id/legal-subject/00164381",
    "DATAHUB_DCAT_PUBLISHER_NAME": (
        "Ministerstvo školstva, výskumu, vývoja a mládeže SR"
    ),
    "DATAHUB_DCAT_CONTACT_NAME": "DataHub Open Data tím",
    "DATAHUB_DCAT_CONTACT_EMAIL": "opendata@example.gov.sk",
    "DATAHUB_DCAT_CATALOG_TITLE": "DataHub Open Data",
    "DATAHUB_DCAT_CATALOG_DESCRIPTION": "Katalóg otvorených dát",
    "DATAHUB_DCAT_DEFAULT_LANGUAGE": "sk",
    "DATAHUB_DCAT_DEFAULT_LANGUAGE_URI": (
        "http://publications.europa.eu/resource/authority/language/SLK"
    ),
    "DATAHUB_DCAT_DEFAULT_SPATIAL_URI": "https://data.gov.sk/id/nuts1/SK0",
    "DATAHUB_DCAT_DEFAULT_DATASET_TYPE_URI": "https://data.gov.sk/def/dataset-type/1",
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
        self._normalize_catalog_metadata(catalog_ref)
        self._normalize_catalog_dataset_links(catalog_ref)

    def graph_from_dataset(self, dataset_dict, dataset_ref):
        self._bind_namespaces()
        dataset_document_ref = self._dataset_document_uri(dataset_dict, dataset_ref)
        self._move_subject(dataset_ref, dataset_document_ref)
        dataset_ref = dataset_document_ref

        self._normalize_publisher(dataset_ref)
        self._normalize_dataset_text(dataset_dict, dataset_ref)
        self._ensure_keywords(dataset_dict, dataset_ref)
        self._ensure_dataset_defaults(dataset_dict, dataset_ref)
        self._ensure_contact_point(dataset_ref)

        distributions = set(self.g.objects(dataset_ref, DCAT.distribution))
        if not distributions:
            distributions = set(self.g.subjects(RDF.type, DCAT.Distribution))

        for distribution in distributions:
            normalized_distribution = self._normalize_distribution_ref(
                dataset_dict, dataset_ref, distribution
            )
            self._normalize_distribution(normalized_distribution)

    def _setting(self, key):
        return os.environ.get(key, DEFAULTS[key])

    def _publisher(self):
        return URIRef(self._setting("DATAHUB_DCAT_PUBLISHER_URI"))

    def _language(self):
        return self._setting("DATAHUB_DCAT_DEFAULT_LANGUAGE")

    def _site_url(self):
        site_url = (
            os.environ.get("CKAN_SITE_URL")
            or os.environ.get("CKAN__SITE_URL")
            or toolkit.config.get("ckan.site_url")
            or ""
        )
        return site_url.rstrip("/")

    def _dataset_name(self, dataset_dict, dataset_ref):
        name = dataset_dict.get("name")
        if name:
            return name

        ref = str(dataset_ref).rstrip("/")
        name = ref.rsplit("/", 1)[-1]
        if name.endswith(".ttl"):
            name = name[:-4]
        return name

    def _dataset_page_uri(self, dataset_dict, dataset_ref):
        return URIRef(
            f"{self._site_url()}/dataset/{self._dataset_name(dataset_dict, dataset_ref)}"
        )

    def _dataset_document_uri(self, dataset_dict, dataset_ref):
        return URIRef(
            f"{self._site_url()}/dataset/{self._dataset_name(dataset_dict, dataset_ref)}.ttl"
        )

    def _resource_document_uri(self, dataset_dict, dataset_ref, resource_ref):
        resource_id = str(resource_ref).rstrip("/").rsplit("/", 1)[-1]
        return URIRef(
            f"{self._site_url()}/dataset/"
            f"{self._dataset_name(dataset_dict, dataset_ref)}/resource/{resource_id}"
        )

    def _package_name_from_ref(self, dataset_ref):
        dataset_id = str(dataset_ref).rstrip("/").rsplit("/", 1)[-1]
        if dataset_id.endswith(".ttl"):
            dataset_id = dataset_id[:-4]

        try:
            package = toolkit.get_action("package_show")(
                {"ignore_auth": True},
                {"id": dataset_id},
            )
        except Exception:
            return dataset_id

        return package.get("name") or dataset_id

    def _replace_literal(self, subject, predicate, value, lang=None):
        self.g.remove((subject, predicate, None))
        if value:
            self.g.add((subject, predicate, Literal(value, lang=lang)))

    def _first_literal_text(self, subject, predicate):
        for value in self.g.objects(subject, predicate):
            if isinstance(value, Literal):
                text = str(value).strip()
                if text:
                    return text
        return None

    def _move_subject(self, old_subject, new_subject):
        if old_subject == new_subject:
            return

        for _, predicate, obj in list(self.g.triples((old_subject, None, None))):
            self.g.remove((old_subject, predicate, obj))
            self.g.add((new_subject, predicate, obj))

        for subject, predicate, _ in list(self.g.triples((None, None, old_subject))):
            self.g.remove((subject, predicate, old_subject))
            self.g.add((subject, predicate, new_subject))

    def _bind_namespaces(self):
        self.g.bind("dcat", DCAT)
        self.g.bind("dcatap", DCATAP)
        self.g.bind("dct", DCTERMS)
        self.g.bind("filetype", FILETYPE)
        self.g.bind("foaf", FOAF)
        self.g.bind("freq", FREQ)
        self.g.bind("language", LANGUAGE)
        self.g.bind("leg", LEG)
        self.g.bind("text", TEXT)
        self.g.bind("theme", THEME)
        self.g.bind("vcard", VCARD)

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
                Literal(
                    self._setting("DATAHUB_DCAT_PUBLISHER_NAME"),
                    lang=self._language(),
                ),
            )
        )

    def _normalize_catalog_metadata(self, catalog_ref):
        lang = self._language()
        self._replace_literal(
            catalog_ref,
            DCTERMS.title,
            self._setting("DATAHUB_DCAT_CATALOG_TITLE"),
            lang=lang,
        )
        self._replace_literal(
            catalog_ref,
            DCTERMS.description,
            self._setting("DATAHUB_DCAT_CATALOG_DESCRIPTION"),
            lang=lang,
        )
        self.g.remove((catalog_ref, DCTERMS.language, None))

        homepage = URIRef(self._site_url())
        self.g.remove((catalog_ref, FOAF.homepage, None))
        self.g.add((catalog_ref, FOAF.homepage, homepage))

        self._ensure_contact_point(catalog_ref)

    def _normalize_catalog_dataset_links(self, catalog_ref):
        existing_links = list(self.g.objects(catalog_ref, DCAT.dataset))
        self.g.remove((catalog_ref, DCAT.dataset, None))
        for dataset_link in existing_links:
            dataset_name = self._package_name_from_ref(dataset_link)
            self.g.add(
                (
                    catalog_ref,
                    DCAT.dataset,
                    URIRef(f"{self._site_url()}/dataset/{dataset_name}.ttl"),
                )
            )

    def _normalize_dataset_text(self, dataset_dict, dataset_ref):
        lang = self._language()
        title = dataset_dict.get("title") or self._first_literal_text(
            dataset_ref, DCTERMS.title
        )
        description = dataset_dict.get("notes") or self._first_literal_text(
            dataset_ref, DCTERMS.description
        )
        self._replace_literal(dataset_ref, DCTERMS.title, title, lang=lang)
        self._replace_literal(dataset_ref, DCTERMS.description, description, lang=lang)

    def _ensure_dataset_defaults(self, dataset_dict, dataset_ref):
        if not list(self.g.objects(dataset_ref, DCTERMS.spatial)):
            self.g.add(
                (
                    dataset_ref,
                    DCTERMS.spatial,
                    URIRef(self._setting("DATAHUB_DCAT_DEFAULT_SPATIAL_URI")),
                )
            )

        if not list(self.g.objects(dataset_ref, DCTERMS.type)):
            self.g.add(
                (
                    dataset_ref,
                    DCTERMS.type,
                    URIRef(self._setting("DATAHUB_DCAT_DEFAULT_DATASET_TYPE_URI")),
                )
            )

        self.g.remove((dataset_ref, DCTERMS.language, None))
        self.g.add(
            (
                dataset_ref,
                DCTERMS.language,
                URIRef(self._setting("DATAHUB_DCAT_DEFAULT_LANGUAGE_URI")),
            )
        )

        landing_page = self._dataset_page_uri(dataset_dict, dataset_ref)
        self.g.remove((dataset_ref, DCAT.landingPage, None))
        self.g.add((dataset_ref, DCAT.landingPage, landing_page))

    def _ensure_keywords(self, dataset_dict, dataset_ref):
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
            keywords.extend(
                str(keyword).strip()
                for keyword in self.g.objects(dataset_ref, DCAT.keyword)
                if str(keyword).strip()
            )

        if not keywords:
            fallback = dataset_dict.get("title") or dataset_dict.get("name")
            if fallback:
                keywords.append(fallback)

        self.g.remove((dataset_ref, DCAT.keyword, None))
        for keyword in keywords:
            self.g.add((dataset_ref, DCAT.keyword, Literal(keyword, lang=self._language())))

    def _ensure_contact_point(self, subject):
        contacts = list(self.g.objects(subject, DCAT.contactPoint))
        if not contacts:
            contacts = [BNode()]
            self.g.add((subject, DCAT.contactPoint, contacts[0]))

        for contact in contacts:
            self._normalize_contact(contact)

    def _normalize_contact(self, contact):
        contact_name = self._setting("DATAHUB_DCAT_CONTACT_NAME")
        contact_email = self._setting("DATAHUB_DCAT_CONTACT_EMAIL")
        if not contact_name and not contact_email:
            return

        self.g.add((contact, RDF.type, VCARD.Organization))
        if contact_name:
            self._replace_literal(contact, VCARD.fn, contact_name, lang=self._language())
        if contact_email and not list(self.g.objects(contact, VCARD.hasEmail)):
            self.g.add((contact, VCARD.hasEmail, URIRef(f"mailto:{contact_email}")))

    def _normalize_distribution_ref(self, dataset_dict, dataset_ref, distribution):
        normalized = self._resource_document_uri(dataset_dict, dataset_ref, distribution)
        self._move_subject(distribution, normalized)
        self.g.remove((dataset_ref, DCAT.distribution, distribution))
        self.g.add((dataset_ref, DCAT.distribution, normalized))
        return normalized

    def _normalize_distribution(self, distribution):
        lang = self._language()
        title = self._first_literal_text(distribution, DCTERMS.title)
        description = self._first_literal_text(distribution, DCTERMS.description)
        self._replace_literal(distribution, DCTERMS.title, title, lang=lang)
        if description:
            self._replace_literal(
                distribution, DCTERMS.description, description, lang=lang
            )

        access_urls = list(self.g.objects(distribution, DCAT.accessURL))
        if access_urls:
            self.g.remove((distribution, DCAT.downloadURL, None))
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
