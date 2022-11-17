# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import transaction
from django.template import Template, RequestContext
from django.http import HttpRequest
from crossref.models import Work


User = get_user_model()


class Tests(TestCase):

    def setUp(self):
        self.doi = "https://doi.org/10.1093/gji/ggz376"
        User.objects.create_superuser('admin', 'admin@test.de', 'admin')
        self.client.login(username='admin', password='admin')

        # This is the data structure from the CrossRef Funder endpoint
        self.funder_data = {
            "id": "501100010956",
            "location": "Germany",
            "name": "Helmholtz-Zentrum Potsdam - Deutsches GeoForschungsZentrum GFZ",
            "alt-names": [
                        "GFZ Helmholtz Centre Potsdam",
                        "GFZ Potsdam",
                        "Helmholtz Center Potsdam German Research Center for Geosciences GFZ",
                        "Deutsche GeoForschungsZentrum GFZ",
                        "German Research Center for Geosciences GFZ",
                        "GeoForschungsZentrum Potsdam",
                        "GFZ German Research Centre for Geosciences",
                        "Deutsche GeoForschungs-Zentrum Potsdam",
                        "GFZ",
                        "German Research Centre for Geosciences",
                        "Deutsche GeoForschungsZentrum",
                        "GeoForschungsZentrum",
                        "Helmholtz-Zentrum Potsdam - Deutsches GeoForschungsZentrum GFZ",
                        "Helmholtz Centre Potsdam - GFZ German Research Centre for Geosciences"
            ],
            "uri": "http://dx.doi.org/10.13039/501100010956",
            "replaces": [],
            "replaced-by": [],
            "tokens": [
                "helmholtz",
                "zentrum",
                "potsdam",
                "deutsches",
                "geoforschungszentrum",
                "gfz",
                "gfz",
                "helmholtz",
                "centre",
                "potsdam",
                "gfz",
                "potsdam",
                "helmholtz",
                "center",
                "potsdam",
                "german",
                "research",
                "center",
                "for",
                "geosciences",
                "gfz",
                "deutsche",
                "geoforschungszentrum",
                "gfz",
                "german",
                "research",
                "center",
                "for",
                "geosciences",
                "gfz",
                "geoforschungszentrum",
                "potsdam",
                "gfz",
                "german",
                "research",
                "centre",
                "for",
                "geosciences",
                "deutsche",
                "geoforschungs",
                "zentrum",
                "potsdam",
                "gfz",
                "german",
                "research",
                "centre",
                "for",
                "geosciences",
                "deutsche",
                "geoforschungszentrum",
                "geoforschungszentrum",
                "helmholtz",
                "zentrum",
                "potsdam",
                "deutsches",
                "geoforschungszentrum",
                "gfz",
                "helmholtz",
                "centre",
                "potsdam",
                "gfz",
                "german",
                "research",
                "centre",
                "for",
                "geosciences"
            ]
        }

        self.work_data = {
            "indexed": {
                "date-parts": [
                    [
                        2022,
                        9,
                        5
                    ]
                ],
                "date-time": "2022-09-05T18:27:56Z",
                "timestamp": 1662402476065
            },
            "reference-count": 72,
            "publisher": "Oxford University Press (OUP)",
            "issue": "2",
            "license": [
                {
                    "start": {
                        "date-parts": [
                            [
                                2019,
                                8,
                                16
                            ]
                        ],
                        "date-time": "2019-08-16T00:00:00Z",
                        "timestamp": 1565913600000
                    },
                    "content-version": "vor",
                    "delay-in-days": 0,
                    "URL": "https://academic.oup.com/journals/pages/open_access/funder_policies/chorus/standard_work_model"
                }
            ],
            "content-domain": {
                "domain": [],
                "crossmark-restriction": False
            },
            "published-print": {
                "date-parts": [
                    [
                        2019,
                        11,
                        1
                    ]
                ]
            },
            "abstract": "<jats:title>SUMMARY</jats:title>\n               <jats:p>Thermal conductivity is a physical parameter crucial to accurately estimating temperature and modelling thermally related processes within the lithosphere. Direct measurements are often impractical due to the high cost of comprehensive sampling or inaccessibility and thereby require indirect estimates. In this study, we report 340 new thermal conductivity measurements on igneous rocks spanning a wide range of compositions using an optical thermal conductivity scanning device. These are supplemented by a further 122 measurements from the literature. Using major element geochemistry and modal mineralogy, we produce broadly applicable empirical relationships between composition and thermal conductivity. Predictive models for thermal conductivity are developed using (in order of decreasing accuracy) major oxide composition, CIPW normative mineralogy and estimated modal mineralogy.</jats:p>\n               <jats:p>Four common mixing relationships (arithmetic, geometric, square-root and harmonic) are tested and, while results are similar, the geometric model consistently produces the best fit. For our preferred model, $k_{\\text{eff}} = \\exp ( 1.72 \\, C_{\\text{SiO}_2} + 1.018 \\, C_{\\text{MgO}} - 3.652 \\, C_{\\text{Na}_2\\text{O}} - 1.791 \\, C_{\\text{K}_2\\text{O}})$, we find that SiO2 is the primary control on thermal conductivity with an RMS of 0.28 W m−1 K−1or ∼10 per cent. Estimates from normative mineralogy work to a similar degree but require a greater number of parameters, while forward and inverse modelling using estimated modal mineralogy produces less than satisfactory results owing to a number of complications. Using our model, we relate thermal conductivity to both P-wave velocity and density, revealing systematic trends across the compositional range. We determine that thermal conductivity can be calculated from P-wave velocity in the range 6–8 km s−1 to within 0.31 W m−1 K−1 using $k({V_p}) = 0.5822 \\, V_p^2 - 8.263 \\, V_p + 31.62$. This empirical model can be used to estimate thermal conductivity within the crust where direct sampling is impractical or simply not possible (e.g. at great depths). Our model represents an improved method for estimating lithospheric conductivity than present formulas which exist only for a limited range of compositions or are limited by infrequently measured parameters.</jats:p>",
            "DOI": "10.1093/gji/ggz376",
            "type": "journal-article",
            "created": {
                        "date-parts": [
                            [
                                2019,
                                8,
                                15
                            ]
                        ],
                    "date-time": "2019-08-15T19:10:40Z",
                "timestamp": 1565896240000
            },
            "page": "1377-1394",
            "source": "Crossref",
            "is-referenced-by-count": 12,
            "title": [
                "A new compositionally based thermal conductivity model for plutonic rocks"
            ],
            "prefix": "10.1093",
            "volume": "219",
            "author": [
                {
                    "ORCID": "http://orcid.org/0000-0003-3762-7336",
                    "authenticated-orcid": False,
                    "given": "S",
                    "family": "Jennings",
                    "sequence": "first",
                    "affiliation": [
                                {
                                    "name": "Department of Earth Sciences, University of Adelaide, North Terrace, SA 5005, Australia"
                                }
                    ]
                },
                {
                    "given": "D",
                    "family": "Hasterok",
                    "sequence": "additional",
                    "affiliation": [
                        {
                                "name": "Department of Earth Sciences, University of Adelaide, North Terrace, SA 5005, Australia"
                        },
                        {
                            "name": "Mawson Centre for Geoscience, University of Adelaide, North Terrace, SA 5005, Australia"
                        }
                    ]
                },
                {
                    "given": "J",
                    "family": "Payne",
                    "sequence": "additional",
                    "affiliation": [
                        {
                                "name": "Department of Earth Sciences, University of Adelaide, North Terrace, SA 5005, Australia"
                        },
                        {
                            "name": "School of Natural and Built Environments, University of South Australia, GPO Box 2471, Adelaide, SA 5001, Australia"
                        }
                    ]
                }
            ],
            "member": "286",
            "published-online": {
                "date-parts": [
                    [
                        2019,
                        8,
                        16
                    ]
                ]
            },
            "reference": [
                {
                    "issue": "15",
                    "key": "2019090604550571700_bib1",
                    "doi-asserted-by": "crossref",
                    "first-page": "2424",
                    "DOI": "10.1093/bioinformatics/btx180",
                    "article-title": "Trainable weka segmentation: a machine learning tool for microscopy pixel classification",
                    "volume": "33",
                    "author": "Arganda-Carreras",
                    "year": "2017",
                            "journal-title": "Bioinformatics"
                },
                {
                    "key": "2019090604550571700_bib2",
                    "volume-title": "PArameter Estimation and Inverse Problems",
                    "author": "Aster",
                    "year": "2011"
                },
                {
                    "key": "2019090604550571700_bib3",
                    "doi-asserted-by": "crossref",
                    "volume-title": "Crustal Heat Flow: A Guide to Measurement and Modelling",
                    "author": "Beardsmore",
                    "year": "2001",
                            "DOI": "10.1017/CBO9780511606021"
                },
                {
                    "issue": "5",
                    "key": "2019090604550571700_bib4",
                    "doi-asserted-by": "publisher",
                    "DOI": "10.1029/2002GC000393",
                    "article-title": "Relationship between seismic P-wave velocity and the composition of anhydrous igneous and meta-igneous rocks",
                    "volume": "4",
                    "author": "Behn",
                    "year": "2003",
                            "journal-title": "Geochem., Geophys., Geosyst."
                },
                {
                    "issue": "8",
                    "key": "2019090604550571700_bib5",
                    "doi-asserted-by": "crossref",
                    "first-page": "529",
                    "DOI": "10.2475/ajs.238.8.529",
                    "article-title": "The thermal conductivity of rocks and its dependence upon temperature and composition",
                    "volume": "238",
                    "author": "Birch",
                    "year": "1940",
                            "journal-title": "Am. J. Sci."
                },
                {
                    "issue": "7",
                    "key": "2019090604550571700_bib6",
                    "doi-asserted-by": "crossref",
                    "first-page": "1145",
                    "DOI": "10.2138/am.2012.3986",
                    "article-title": "Heat transfer in plagioclase feldspars",
                    "volume": "97",
                    "author": "Branlund",
                    "year": "2012",
                            "journal-title": "Am. Mineral."
                },
                {
                    "key": "2019090604550571700_bib7",
                    "article-title": "Structural, geochemical and isotopic investigation of granitoids within the central area of the eastern Weekeroo Inlier, Olary Domain, South Australia",
                    "volume-title": "BSc (Hons) thesis",
                    "author": "Brett",
                    "year": "1998"
                },
                {
                    "issue": "3",
                    "key": "2019090604550571700_bib8",
                    "doi-asserted-by": "crossref",
                    "first-page": "525",
                    "DOI": "10.1111/j.1365-246X.1989.tb02287.x",
                    "article-title": "Mineralogy, porosity and fluid control on thermal conductivity of sedimentary rocks",
                    "volume": "98",
                    "author": "Brigaud",
                    "year": "1989",
                            "journal-title": "Geophys. J. Int."
                },
                {
                    "key": "2019090604550571700_bib9",
                    "volume-title": "Practical Handbook of Physical Properties of Rocks and Minerals",
                    "author": "Carmichael",
                    "year": "1989"
                },
                {
                    "key": "2019090604550571700_bib10",
                    "first-page": "305",
                    "article-title": "Thermal conductivity and specific heat of minerals and rocks",
                    "volume-title": "Landolt-Bornstein; Zahlenwerte und Funktionen aus Naturwissenschaften und Technik",
                    "author": "Cermak",
                    "year": "1982"
                },
                {
                    "key": "2019090604550571700_bib11",
                    "doi-asserted-by": "crossref",
                    "first-page": "1",
                    "DOI": "10.1016/j.geothermics.2018.03.011",
                    "article-title": "Evaluate best-mixing model for estimating thermal conductivity for granitoids from mineralogy: a case study for the granitoids of the bundelkhand craton, central india",
                    "volume": "75",
                    "author": "Chopra",
                    "year": "2018",
                            "journal-title": "Geothermics"
                },
                {
                    "key": "2019090604550571700_bib12",
                    "article-title": "Petrology of the plutonic rocks of the Macquarie Island Complex",
                    "volume-title": "PhD thesis",
                    "author": "Christodoulou",
                    "year": "1990"
                },
                {
                    "key": "2019090604550571700_bib13",
                    "first-page": "493",
                    "article-title": "Geothermal energy",
                    "volume": "3",
                    "author": "Clauser",
                    "year": "2006",
                            "journal-title": "Landolt-B”ornstein, group VIII: advanced materials and technologies"
                },
                {
                    "key": "2019090604550571700_bib14",
                    "first-page": "1431",
                    "volume-title": "Thermal Storage and Transport Properties of Rocks, II: Thermal Conductivity and Diffusivity",
                    "author": "Clauser",
                    "year": "2011"
                },
                {
                    "key": "2019090604550571700_bib15",
                    "first-page": "105",
                    "article-title": "Thermal conductivity of rocks and minerals",
                    "volume-title": "Rock Physics and Phase Relations: A Handbook of Physical Constants",
                    "author": "Clauser",
                    "year": "1995"
                },
                {
                    "issue": "B5",
                    "key": "2019090604550571700_bib16",
                    "doi-asserted-by": "publisher",
                    "DOI": "10.1029/2006JB004755",
                    "article-title": "Thermal conductivity anisotropy of metasedimentary and igneous rocks",
                    "volume": "112",
                    "author": "Davis",
                    "year": "2007",
                            "journal-title": "J. geophys. Res.: Solid Earth"
                },
                {
                    "key": "2019090604550571700_bib17",
                    "doi-asserted-by": "crossref",
                    "volume-title": "Thermal Conductivity of Some Rock-Forming Minerals: A Tabulation",
                    "author": "Diment",
                    "year": "1988",
                            "DOI": "10.3133/ofr88690"
                },
                {
                    "key": "2019090604550571700_bib18",
                    "article-title": "The geology, petrology, geochemistry and isotope geology of the eastern St Peter Suite, western Gawler Graton, South Australia / Melissa B. Dove",
                    "volume-title": "BSc (Hons) thesis",
                    "author": "Dove",
                    "year": "1997"
                },
                {
                    "key": "2019090604550571700_bib19",
                    "volume-title": "Properties of Anisotropic Solid-State Materials: Thermal and Electric Properties",
                    "author": "Dreyer",
                    "year": "1974"
                },
                {
                    "key": "2019090604550571700_bib20",
                    "first-page": "35",
                    "article-title": "The estimation of rock thermal conductivity from mineral content–an assessment of techniques",
                    "volume": "1",
                    "author": "Drury",
                    "year": "1983",
                            "journal-title": "Zentralbl. Geol. Palaeontol."
                },
                {
                    "key": "2019090604550571700_bib21",
                    "first-page": "99",
                    "volume-title": "Thermal Properties of Rocks and Density of Fluids",
                    "author": "Eppelbaum",
                    "year": "2014"
                },
                {
                    "issue": "Supplement C",
                    "key": "2019090604550571700_bib22",
                    "doi-asserted-by": "crossref",
                    "first-page": "255",
                    "DOI": "10.1016/j.geothermics.2014.06.003",
                    "article-title": "Study cases of thermal conductivity prediction from p-wave velocity and porosity",
                    "volume": "53",
                    "author": "Esteban",
                    "year": "2015",
                            "journal-title": "Geothermics"
                },
                {
                    "key": "2019090604550571700_bib23",
                    "article-title": "A geochemical and isotopic study of the mafic and intermediate rocks in the Olary Province, South Australia - Magma Discrimination and Geochronological Framework",
                    "volume-title": "BSc (Hons) thesis",
                    "author": "Freeman",
                    "year": "1995"
                },
                {
                    "issue": "10",
                    "key": "2019090604550571700_bib25",
                    "doi-asserted-by": "crossref",
                    "first-page": "8602",
                    "DOI": "10.1029/2018JB016287",
                    "article-title": "Calculation of thermal conductivity of low-porous, isotropic plutonic rocks of the crust at ambient conditions from modal mineralogy and porosity: a viable alternative for direct measurement?",
                    "volume": "123",
                    "author": "Fuchs",
                    "year": "2018",
                            "journal-title": "J. geophys. Res.: Solid Earth"
                },
                {
                    "issue": "Supplement C",
                    "key": "2019090604550571700_bib24",
                    "doi-asserted-by": "crossref",
                    "first-page": "40",
                    "DOI": "10.1016/j.geothermics.2013.02.002",
                    "article-title": "Evaluation of common mixing models for calculating bulk thermal conductivity of sedimentary rocks: correction charts and new conversion equations",
                    "volume": "47",
                    "author": "Fuchs",
                    "year": "2013",
                            "journal-title": "Geothermics"
                },
                {
                    "issue": "Supplement C",
                    "key": "2019090604550571700_bib26",
                    "doi-asserted-by": "crossref",
                    "first-page": "50",
                    "DOI": "10.1016/j.jappgeo.2011.10.005",
                    "article-title": "New approaches for the relationship between compressional wave velocity and thermal conductivity",
                    "volume": "76",
                    "author": "Gegenhuber",
                    "year": "2012",
                            "journal-title": "J. appl. Geophys."
                },
                {
                    "key": "2019090604550571700_bib27",
                    "doi-asserted-by": "crossref",
                    "first-page": "61",
                    "DOI": "10.1016/j.geothermics.2016.11.007",
                    "article-title": "Using seismic data to estimate the spatial distribution of rock thermal conductivity at reservoir scale",
                    "volume": "66",
                    "author": "Gu",
                    "year": "2017",
                            "journal-title": "Geothermics"
                },
                {
                    "issue": "7-8",
                    "key": "2019090604550571700_bib28",
                    "doi-asserted-by": "crossref",
                    "first-page": "1042",
                    "DOI": "10.1016/j.ijrmms.2005.05.015",
                    "article-title": "Thermal conductivity from core and well log data",
                    "volume": "42",
                    "author": "Hartmann",
                    "year": "2005",
                            "journal-title": "Int. J. Rock Mech. Min. Sci."
                },
                {
                    "issue": "1",
                    "key": "2019090604550571700_bib29",
                    "doi-asserted-by": "crossref",
                    "first-page": "59",
                    "DOI": "10.1016/j.epsl.2011.04.034",
                    "article-title": "Heat production and geotherms for the continental lithosphere",
                    "volume": "307",
                    "author": "Hasterok",
                    "year": "2011",
                            "journal-title": "Earth planet. Sci. Lett."
                },
                {
                    "issue": "6",
                    "key": "2019090604550571700_bib31",
                    "doi-asserted-by": "crossref",
                    "first-page": "1777",
                    "DOI": "10.1016/j.gsf.2017.10.012",
                    "article-title": "On the radiogenic heat production of metamorphic, igneous, and sedimentary rocks",
                    "volume": "9",
                    "author": "Hasterok",
                    "year": "2018",
                            "journal-title": "Geosci. Front."
                },
                {
                    "issue": "5",
                    "key": "2019090604550571700_bib30",
                    "doi-asserted-by": "crossref",
                    "first-page": "919",
                    "DOI": "10.1016/j.gsf.2017.03.006",
                    "article-title": "On the radiogenic heat production of igneous rocks",
                    "volume": "8",
                    "author": "Hasterok",
                    "year": "2017",
                            "journal-title": "Geosci. Front."
                },
                {
                    "key": "2019090604550571700_bib32",
                    "article-title": "The petrology and geochemistry of the upper South-East Granites",
                    "volume-title": "Thesis",
                    "author": "Henstridge",
                    "year": "1970"
                },
                {
                    "key": "2019090604550571700_bib33",
                    "article-title": "The Granitoids and migmatites of the Monarto Area",
                    "volume-title": "Thesis",
                    "author": "Hoesni",
                    "year": "1985"
                },
                {
                    "key": "2019090604550571700_bib34",
                    "volume-title": "CIPW Norm Calculation Program",
                    "author": "Hollocher",
                    "year": "2004"
                },
                {
                    "issue": "5",
                    "key": "2019090604550571700_bib35",
                    "doi-asserted-by": "crossref",
                    "first-page": "1278",
                    "DOI": "10.1029/JB076i005p01278",
                    "article-title": "Thermal conductivity of rock-forming minerals",
                    "volume": "76",
                    "author": "Horai",
                    "year": "1971",
                            "journal-title": "J. geophys. Res."
                },
                {
                    "issue": "3",
                    "key": "2019090604550571700_bib36",
                    "doi-asserted-by": "crossref",
                    "first-page": "292",
                    "DOI": "10.1016/0031-9201(89)90077-0",
                    "article-title": "The effect of pressure on the thermal conductivity of silicate rocks up to 12 kbar",
                    "volume": "55",
                    "author": "Horai",
                    "year": "1989",
                            "journal-title": "Phys. Earth planet. Inter."
                },
                {
                    "key": "2019090604550571700_bib37",
                    "doi-asserted-by": "crossref",
                    "first-page": "151",
                    "DOI": "10.1016/0031-9201(72)90084-2",
                    "article-title": "Thermal conductivity of nineteen igneous rocks, I application of the needle probe method to the measurement of the thermal conductivity of rock",
                    "volume": "5",
                    "author": "Horai",
                    "year": "1972",
                            "journal-title": "Phys. Earth planet. Inter."
                },
                {
                    "key": "2019090604550571700_bib38",
                    "doi-asserted-by": "crossref",
                    "first-page": "157",
                    "DOI": "10.1016/0031-9201(72)90085-4",
                    "article-title": "Thermal conductivity of nineteen igneous rocks, II estimation of the thermal conductivity of rock from the mineral and chemical compositions",
                    "volume": "5",
                    "author": "Horai",
                    "year": "1972",
                            "journal-title": "Phys. Earth planet. Inter."
                },
                {
                    "key": "2019090604550571700_bib39",
                    "article-title": "The petrology, geochemistry and geochronology of the felsic alkaline suite of the Eastern Yilgarn Block",
                    "volume-title": "PhD thesis",
                    "author": "Johnson",
                    "year": "1991"
                },
                {
                    "issue": "2",
                    "key": "2019090604550571700_bib40",
                    "doi-asserted-by": "crossref",
                    "first-page": "595",
                    "DOI": "10.1029/JB073i002p00595",
                    "article-title": "Thermal diffusivity measurement of rock-forming minerals from 300○ to 1100○k",
                    "volume": "73",
                    "author": "Kanamori",
                    "year": "1968",
                            "journal-title": "J. geophys. Res."
                },
                {
                    "key": "2019090604550571700_bib41",
                    "article-title": "Petrogenesis of the Western St Peter Suite, Western Gawler Craton, South Australia - a petrological, geochemical and isotopic investigation",
                    "volume-title": "PhD thesis",
                    "author": "Knight",
                    "year": "1997"
                },
                {
                    "key": "2019090604550571700_bib42",
                    "article-title": "Petrogenesis of high heat producing granite: implication for Mt Painter Province",
                    "volume-title": "PhD thesis",
                    "author": "Kromkhun",
                    "year": "2010"
                },
                {
                    "key": "2019090604550571700_bib44",
                    "article-title": "Petrology, structure and stratigraphy of the Willyama Supergroup and Olarian granitoids, west of Plumbago Homestead",
                    "volume-title": "PhD thesis",
                    "author": "Leah",
                    "year": "1985"
                },
                {
                    "issue": "5",
                    "key": "2019090604550571700_bib43",
                    "doi-asserted-by": "crossref",
                    "first-page": "825",
                    "DOI": "10.1144/gsjgs.148.5.0825",
                    "article-title": "The iugs systematics of igneous rocks",
                    "volume": "148",
                    "author": "Le Bas",
                    "year": "1991",
                            "journal-title": "J. Geol. Soc."
                },
                {
                    "issue": "24",
                    "key": "2019090604550571700_bib45",
                    "doi-asserted-by": "crossref",
                    "first-page": "3396",
                    "DOI": "10.1088/0022-3727/37/24/007",
                    "article-title": "Prediction of thermal conductivity of granite rocks from porosity and density data at normal temperature and pressure: in situthermal conductivity measurements",
                    "volume": "37",
                    "author": "Maqsood",
                    "year": "2004",
                            "journal-title": "J. Phys. D: Appl. Phys."
                },
                {
                    "key": "2019090604550571700_bib46",
                    "volume-title": "Spravocnik (kadastr.) fiziceskich svoistv gornich porod",
                    "author": "Melnikov",
                    "year": "1975"
                },
                {
                    "issue": "3-4",
                    "key": "2019090604550571700_bib47",
                    "doi-asserted-by": "crossref",
                    "first-page": "215",
                    "DOI": "10.1016/0012-8252(94)90029-9",
                    "article-title": "Naming materials in the magma/igneous rock system",
                    "volume": "37",
                    "author": "Middlemost",
                    "year": "1994",
                            "journal-title": "Earth-Sci. Rev."
                },
                {
                    "key": "2019090604550571700_bib48",
                    "doi-asserted-by": "crossref",
                    "first-page": "135",
                    "DOI": "10.1016/j.jappgeo.2017.04.002",
                    "article-title": "Determining the relationship of thermal conductivity and compressional wave velocity of common rock types as a basis for reservoir characterization",
                    "volume": "140",
                    "author": "Mielke",
                    "year": "2017",
                            "journal-title": "J. appl. Geophys."
                },
                {
                    "key": "2019090604550571700_bib49",
                    "doi-asserted-by": "crossref",
                    "first-page": "137",
                    "DOI": "10.1016/j.tecto.2014.04.007",
                    "article-title": "Effect of water saturation on rock thermal conductivity measurements",
                    "volume": "626",
                    "author": "Nagaraju",
                    "year": "2014",
                            "journal-title": "Tectonophysics"
                },
                {
                    "key": "2019090604550571700_bib50",
                    "article-title": "Isotopic and geochemical characteristics of the British Empire Granite as indicators of magma provenance and processes of melt generation in the Mount Painter Inlier",
                    "volume-title": "BA thesis",
                    "author": "Neumann",
                    "year": "1996"
                },
                {
                    "key": "2019090604550571700_bib51",
                    "article-title": "Petrology of Early Proterozoic granitoids in the Halls Creek mobile zone",
                    "volume-title": "PhD thesis",
                    "author": "Ogasawara",
                    "year": "1996"
                },
                {
                    "key": "2019090604550571700_bib53",
                    "doi-asserted-by": "crossref",
                    "first-page": "1137",
                    "DOI": "10.1007/978-3-0348-8083-1_21",
                    "article-title": "Interrelations between thermal conductivity and other physical properties of rocks: experimental data",
                    "volume-title": "Thermo-Hydro-Mechanical Coupling in Fractured Rock",
                    "author": "Popov",
                    "year": "2003"
                },
                {
                    "issue": "2",
                    "key": "2019090604550571700_bib54",
                    "doi-asserted-by": "crossref",
                    "first-page": "253",
                    "DOI": "10.1016/S0375-6505(99)00007-3",
                    "article-title": "Characterization of rock thermal conductivity by high-resolution optical scanning",
                    "volume": "28",
                    "author": "Popov",
                    "year": "1999",
                            "journal-title": "Geothermics"
                },
                {
                    "issue": "20",
                    "key": "2019090604550571700_bib55",
                    "doi-asserted-by": "crossref",
                    "first-page": "2199",
                    "DOI": "10.1029/93GL02135",
                    "article-title": "Estimation of thermal conductivity from the mineral composition: influence of fabric and anisotropy",
                    "volume": "20",
                    "author": "Pribnow",
                    "year": "1993",
                            "journal-title": "Geophys. Res. Lett."
                },
                {
                    "key": "2019090604550571700_bib57",
                    "doi-asserted-by": "crossref",
                    "first-page": "138",
                    "DOI": "10.1016/j.geothermics.2015.01.007",
                    "article-title": "Tracking the thermal properties of the lower continental crust: measured versus calculated thermal conductivity of high-grade metamorphic rocks (southern granulite province, india)",
                    "volume": "55",
                    "author": "Ray",
                    "year": "2015",
                            "journal-title": "Geothermics"
                },
                {
                    "issue": "3",
                    "key": "2019090604550571700_bib56",
                    "doi-asserted-by": "crossref",
                    "first-page": "241",
                    "DOI": "10.1016/j.epsl.2006.09.010",
                    "article-title": "Thermal diffusivity of felsic to mafic granulites at elevated temperatures",
                    "volume": "251",
                    "author": "Ray",
                    "year": "2006",
                            "journal-title": "Earth planet. Sci. Lett."
                },
                {
                    "key": "2019090604550571700_bib58",
                    "article-title": "Geochronological and geochemical constraints on the lithospheric evolution of the Arabian shield, Saudi Arabia: understanding plutonic rock petrogenesis in an accretionary Orogen",
                    "volume-title": "PhD thesis",
                    "author": "Robinson",
                    "year": "2014"
                },
                {
                    "key": "2019090604550571700_bib2_358_1567495683713",
                    "article-title": "The GEOROC database as part of a growing geoinformatics network",
                    "author": "Sarbas",
                    "year": "2008",
                    "journal-title": "Geoinformatics"
                },
                {
                    "issue": "16",
                    "key": "2019090604550571700_bib59",
                    "doi-asserted-by": "crossref",
                    "first-page": "4064",
                    "DOI": "10.1029/JZ070i016p04064",
                    "article-title": "The thermal conductivity of fifteen feldspar specimens",
                    "volume": "70",
                    "author": "Sass",
                    "year": "1965",
                            "journal-title": "J. geophys. Res."
                },
                {
                    "issue": "7",
                    "key": "2019090604550571700_bib60",
                    "doi-asserted-by": "crossref",
                    "first-page": "676",
                    "DOI": "10.1038/nmeth.2019",
                    "article-title": "Fiji: an open-source platform for biological-image analysis",
                    "volume": "9",
                    "author": "Schindelin",
                    "year": "2012",
                            "journal-title": "Nat. Methods"
                },
                {
                    "issue": "7",
                    "key": "2019090604550571700_bib62",
                    "doi-asserted-by": "crossref",
                    "first-page": "671",
                    "DOI": "10.1038/nmeth.2089",
                    "article-title": "NIH image to ImageJ: 25 years of image analysis",
                    "volume": "9",
                    "author": "Schneider",
                    "year": "2012",
                            "journal-title": "Nat. Methods"
                },
                {
                    "key": "2019090604550571700_bib63",
                    "first-page": "109",
                    "volume-title": "Density",
                    "author": "Schön",
                    "year": "2015"
                },
                {
                    "key": "2019090604550571700_bib61",
                    "first-page": "369",
                    "volume-title": "Thermal Properties",
                    "author": "Schön",
                    "year": "2015"
                },
                {
                    "issue": "1",
                    "key": "2019090604550571700_bib64",
                    "doi-asserted-by": "crossref",
                    "first-page": "161",
                    "DOI": "10.1016/S0040-1951(98)00037-7",
                    "article-title": "Temperature dependence of thermal transport properties of crystalline rocks—a general law",
                    "volume": "291",
                    "author": "Seipold",
                    "year": "1998",
                            "journal-title": "Tectonophysics"
                },
                {
                    "key": "2019090604550571700_bib1_865_1567490045637",
                    "doi-asserted-by": "crossref",
                    "first-page": "773",
                    "DOI": "10.1007/BF01820841",
                    "article-title": "Classification and nomenclature of plutonic rocks recommendations of the IUGS subcommission on the systematics of rocks",
                    "volume": "63",
                    "author": "",
                    "year": "1974",
                            "journal-title": "Geol. Rundsch."
                },
                {
                    "issue": "6",
                    "key": "2019090604550571700_bib65",
                    "doi-asserted-by": "crossref",
                    "first-page": "1023",
                    "DOI": "10.1016/j.ijrmms.2009.01.010",
                    "article-title": "Estimation of thermal conductivity and its spatial variability in igneous rocks from in situ density logging",
                    "volume": "46",
                    "author": "Sundberg",
                    "year": "2009",
                            "journal-title": "Int. J. Rock Mech. Min. Sci."
                },
                {
                    "issue": "1-2",
                    "key": "2019090604550571700_bib66",
                    "doi-asserted-by": "crossref",
                    "first-page": "75",
                    "DOI": "10.1016/j.enggeo.2005.12.001",
                    "article-title": "Porosity in crystalline rocks – a matter of scale",
                    "volume": "84",
                    "author": "Tullborg",
                    "year": "2006",
                            "journal-title": "Eng. Geol."
                },
                {
                    "issue": "1",
                    "key": "2019090604550571700_bib67",
                    "doi-asserted-by": "crossref",
                    "first-page": "167",
                    "DOI": "10.1016/0040-1951(94)00225-X",
                    "article-title": "Thermal conductivity estimation in sedimentary basins",
                    "volume": "244",
                    "author": "Vasseur",
                    "year": "1995",
                            "journal-title": "Tectonophysics"
                },
                {
                    "issue": "9",
                    "key": "2019090604550571700_bib68",
                    "doi-asserted-by": "crossref",
                    "first-page": "499",
                    "DOI": "10.1016/S1474-7065(03)00069-X",
                    "article-title": "Influence of temperature on thermal conductivity, thermal capacity and thermal diffusivity for different types of rock",
                    "volume": "28",
                    "author": "Vosteen",
                    "year": "2003",
                            "journal-title": "Phys. Chem. Earth, Parts A/B/C"
                },
                {
                    "issue": "B6",
                    "key": "2019090604550571700_bib69",
                    "doi-asserted-by": "crossref",
                    "first-page": "9209",
                    "DOI": "10.1029/JB095iB06p09209",
                    "article-title": "Thermophysical properties of the earth’s crust: in situ measurements from continental and ocean drilling",
                    "volume": "95",
                    "author": "Williams",
                    "year": "1990",
                            "journal-title": "J. geophys. Res.: Solid Earth"
                },
                {
                    "issue": "9",
                    "key": "2019090604550571700_bib70",
                    "doi-asserted-by": "crossref",
                    "first-page": "1688",
                    "DOI": "10.1063/1.1728419",
                    "article-title": "Thermal conductivity of porous media. I. Unconsolidated sands",
                    "volume": "32",
                    "author": "Woodside",
                    "year": "1961",
                            "journal-title": "J. Appl. Phys."
                },
                {
                    "issue": "4",
                    "key": "2019090604550571700_bib52",
                    "doi-asserted-by": "crossref",
                    "first-page": "703",
                    "DOI": "10.1016/j.ijrmms.2004.01.002",
                    "article-title": "Determination of the thermal conductivity of rock from p-wave velocity",
                    "volume": "41",
                    "author": "Özkahraman",
                    "year": "2004",
                            "journal-title": "Int. J. Rock Mech. Min. Sci."
                }
            ],
            "container-title": [
                "Geophysical Journal International"
            ],
            "language": "en",
            "link": [
                {
                        "URL": "http://academic.oup.com/gji/advance-article-pdf/doi/10.1093/gji/ggz376/29173408/ggz376.pdf",
                        "content-type": "application/pdf",
                        "content-version": "am",
                        "intended-application": "syndication"
                },
                {
                    "URL": "http://academic.oup.com/gji/article-pdf/219/2/1377/29717570/ggz376.pdf",
                    "content-type": "unspecified",
                    "content-version": "vor",
                    "intended-application": "similarity-checking"
                }
            ],
            "deposited": {
                "date-parts": [
                    [
                        2019,
                        9,
                        6
                    ]
                ],
                "date-time": "2019-09-06T08:56:14Z",
                "timestamp": 1567760174000
            },
            "score": 28.576984,
            "resource": {
                "primary": {
                    "URL": "https://academic.oup.com/gji/article/219/2/1377/5550734"
                }
            },
            "issued": {
                "date-parts": [
                    [
                        2019,
                        8,
                        16
                    ]
                ]
            },
            "references-count": 72,
            "journal-issue": {
                "issue": "2",
                "published-print": {
                    "date-parts": [
                        [
                            2019,
                            11,
                            1
                        ]
                    ]
                }
            },
            "URL": "http://dx.doi.org/10.1093/gji/ggz376",
            "ISSN": [
                "0956-540X",
                "1365-246X"
            ],
            "issn-type": [
                {
                    "value": "0956-540X",
                    "type": "print"
                },
                {
                    "value": "1365-246X",
                    "type": "electronic"
                }
            ],
            "subject": [
                "Geochemistry and Petrology",
                "Geophysics"
            ],
            "published-other": {
                "date-parts": [
                    [
                        2019,
                        11
                    ]
                ]
            },
            "published": {
                "date-parts": [
                    [
                        2019,
                        8,
                        16
                    ]
                ]
            }
        }

    # def test_add_from_crossref_url(self):
    # 	self.assertEqual(self.client.get('/admin/crossref/work/add-from-crossref', follow=True).status_code, 200)

    def test_import_bibtex_url(self):
        self.assertEqual(
            self.client.get(
                '/admin/crossref/work/import-bibtex',
                follow=True).status_code,
            200)

    def test_work_delete_relationship_fields(self):
        self.assertEqual(True, False)
