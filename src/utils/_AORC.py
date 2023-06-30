from rdflib.namespace import DefinedNamespace, Namespace
from rdflib import URIRef


class AORC(DefinedNamespace):
    # Classes
    CommandList: URIRef
    CompositeDataset: URIRef
    DockerCompose: URIRef
    DockerContainer: URIRef
    DockerImage: URIRef
    DockerProcess: URIRef
    MirrorDataset: URIRef
    RFC: URIRef
    SourceDataset: URIRef
    TranspositionDataset: URIRef
    # Object Properties
    hasRFC: URIRef
    maxPrecipitationPoint: URIRef
    normalizedBy: URIRef
    transpositionRegion: URIRef
    watershedRegion: URIRef
    # Data Properties
    cellCount: URIRef
    maxPrecipitation: URIRef
    meanPrecipitation: URIRef
    normalizedMeanPrecipitation: URIRef
    sumPrecipitation: URIRef

    _NS = Namespace("https://raw.githubusercontent.com/Dewberry/blobfish/v0.9/semantics/rdf/aorc.ttl")
