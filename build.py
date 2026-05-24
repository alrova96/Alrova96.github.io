#!/usr/bin/env python3
"""
Static Site Generator for Alejandro Román's Website
Generates a modern, elegant website from templates
"""

import os
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import json

# Define directories
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'
OUTPUT_DIR = BASE_DIR / 'docs'

# Site configuration
SITE_CONFIG = {
    'title': 'Alejandro Román',
    'description': 'Postdoctoral Researcher at ICMAN-CSIC',
    'author': 'Alejandro Román',
    'email': 'mail.a.roman@csic.es',
    'twitter': 'https://twitter.com/a_roman_4',
    'linkedin': 'https://www.linkedin.com/in/alejandro-rom%C3%A1n-v%C3%A1zquez/',
    'github': 'https://github.com/alrova96',
    'researchgate': 'https://www.researchgate.net/profile/Alejandro-Roman-9',
    'google_scholar': 'https://scholar.google.es/citations?view_op=list_works&hl=es&hl=es&user=rOnlIMcAAAAJ',
    'orcid': 'https://orcid.org/my-orcid?orcid=0000-0002-8868-9302',
}

# Publications data (sorted by date, most recent first)
PUBLICATIONS = [
    {
        'title': 'Unveiling the large coverage of red snow algae blooms in antarctic coastal snowfields',
        'authors': '<strong>Alejandro Román</strong>, Gabriel Navarro, Luis Barbero, Beatriz Fernández-Marín, José I. García-Plazaola, Enrique González-Ortegón, Isabel Caballero & Antonio Tovar-Sánchez',
        'journal': 'Communications Earth & Environment',
        'journal_logo': 'commun_logo.png',
        'image': 'snowalgae.png',
        'date': '2026 - Communications Earth & Environment',
        'doi': 'https://doi.org/10.1038/s43247-025-03156-6',
        'pdf': 'https://www.nature.com/articles/s43247-025-03156-6.pdf'
    },
    {
        'title': 'UAV imagery in natural disasters: Real-time damage assessment of flash flooding events',
        'authors': '<strong>Alejandro Román</strong>, Antonio Tovar-Sánchez, Manuel Larrad, Jorge Rubiano-Sánchez, José M. Zafra, Rafael Piñeiro, Antonio Castillo, Francisco A. López, Ana L. Vela, Ana Allende, Gema Sánchez, Antonio Martínez-Alonso, David Samper, Juan Carlos García, Iván Galindo & Gabriel Navarro',
        'journal': 'Ecological Informatics',
        'journal_logo': 'ecoinf_logo.png',
        'image': 'dana.png',
        'date': '2025 - Ecological Informatics',
        'doi': 'https://doi.org/10.1016/j.ecoinf.2025.103433',
        'pdf': 'https://www.sciencedirect.com/science/article/pii/S1574954125000093/pdf'
    },
    {
        'title': 'LiDAR-based topographic data for the coastline of Port Foster (Deception Island, Antarctica)',
        'authors': '<strong>Alejandro Román</strong>, Antonio Tovar-Sánchez, Manuel Larrad, Fernando Alva & Gabriel Navarro',
        'journal': 'Scientific Data',
        'journal_logo': 'scidata_logo.png',
        'image': 'lidar.png',
        'date': '2025 - Scientific Data',
        'doi': 'https://doi.org/10.1038/s41597-025-05726-x',
        'pdf': 'https://www.nature.com/articles/s41597-025-05726-x.pdf'
    },
    {
        'title': 'Air-water CO2 exchange in transformed saltmarshes for different uses and under various management models',
        'authors': 'Samuel Amaya-Vías, Susana Flecha, <strong>Alejandro Román</strong>, Soledad Haro, Jose Luis Oviedo, Gabriel Navarro, Gabriel M. Arroyo & I. Emma Huertas',
        'journal': 'Journal of Environmental Management',
        'journal_logo': 'jem_logo.png',
        'image': 'ch4.png',
        'date': '2025 - Journal of Environmental Management',
        'doi': 'https://doi.org/10.1016/j.jenvman.2025.125188',
        'pdf': 'https://www.sciencedirect.com/science/article/pii/S0301479725002178/pdf'
    },
    {
        'title': 'Mapping intertidal microphytobenthic biomass with very high-resolution remote sensing imagery in an estuarine system',
        'authors': '<strong>Alejandro Román</strong>, Simon Oiry, Bede F.R. Davies, Philippe Rosa, Pierre Gernez, Antonio Tovar-Sánchez, Gabriel Navarro, Vona Méléder & Laurent Barillé',
        'journal': 'Science of The Total Environment',
        'journal_logo': 'stoten_logo.png',
        'image': 'mpb_stoten.PNG',
        'doi': 'https://doi.org/10.1016/j.scitotenv.2024.177025',
        'pdf': 'https://www.sciencedirect.com/science/article/pii/S0048969724071821/pdf',
        'year': 2024,
        'date': '2024 - Science of The Total Environment'
    },
    {
        'title': 'Assessing topographic features and population abundance in an Antarctic penguin colony through UAV-based deep-learning models',
        'authors': 'Oleg Belyaev, <strong>Alejandro Román</strong>, Josabel Belliure, Gabriel Navarro, Luis Barbero & Antonio Tovar-Sánchez',
        'journal': 'International Journal of Applied Earth Observation and Geoinformation',
        'journal_logo': 'jag_logo.png',
        'image': 'penguins_oleg.PNG',
        'date': '2024 - Int. Journal of Applied Earth Observation and Geoinformation',
        'doi': 'https://doi.org/10.1016/j.jag.2024.104124',
        'pdf': 'https://www.sciencedirect.com/science/article/pii/S1569843224004783/pdf'
    },
    {
        'title': 'Intertidal seagrass extent from Sentinel-2 time-series show distinct trajectories in Western Europe',
        'authors': 'Bede Ffinian Rowe Davies, Simon Oiry, Philippe Rosa, Maria Laura Zoffoli, Ana I.Sousa, Oliver R.Thomas, Dan A.Smale, Melanie C.Austen, Lauren Biermann, Martin J.Attrill, <strong>Alejandro Román</strong>, Gabriel Navarro, Anne-Laure Barillé, Nicolas Harin, Daniel Clewley, Victor Martinez-Vicente, Pierre Gernez & Laurent Barillé',
        'journal': 'Remote Sensing of Environment',
        'journal_logo': 'RSE_logo.png',
        'image': 'david_rse.PNG',
        'date': '2024 - Remote Sensing of Environment',
        'doi': 'https://doi.org/10.1016/j.rse.2024.114340',
        'pdf': 'https://www.sciencedirect.com/science/article/pii/S0034425724003584/pdf'
    },
    {
        'title': 'A sentinel watching over inter-tidal seagrass phenology across Western Europe and North Africa',
        'authors': 'Bede Ffinian Rowe Davies, Simon Oiry, Philippe Rosa, Maria Laura Zoffoli, Ana I.Sousa, Oliver R.Thomas, Dan A.Smale, Melanie C.Austen, Lauren Biermann, Martin J.Attrill, <strong>Alejandro Román</strong>, Gabriel Navarro, Anne-Laure Barillé, Nicolas Harin, Daniel Clewley, Victor Martinez-Vicente, Pierre Gernez & Laurent Barillé',
        'journal': 'Nature Communications Earth & Environment',
        'journal_logo': 'commun_logo.png',
        'image': 'david_commun.PNG',
        'date': '2024 - Communications Earth & Environment',
        'doi': 'https://doi.org/10.1038/s43247-024-01543-z',
        'pdf': 'https://www.nature.com/articles/s43247-024-01543-z.pdf'
    },
    {
        'title': 'ShetlandsUAVmetry: unmanned aerial vehicle-based photogrammetric dataset for Antarctic environmental research',
        'authors': '<strong>Alejandro Román</strong>, Gabriel Navarro, Antonio Tovar-Sánchez, Pedro Zarandona, David Roque-Atienza & Luis Barbero',
        'journal': 'Scientific Data',
        'journal_logo': 'scidata_logo.png',
        'image': 'shetlandsUAVmetry.png',
        'date': '2024 - Scientific Data',
        'doi': 'https://doi.org/10.1038/s41597-024-03045-1',
        'pdf': 'https://www.nature.com/articles/s41597-024-03045-1.pdf'
    },
    {
        'title': 'Enhancing Georeferencing and Mosaicking Techniques over Water Surfaces with High-Resolution Unmanned Aerial Vehicle (UAV) Imagery',
        'authors': '<strong>Alejandro Román</strong>, Sergio Heredia, Anna E. Windle, Antonio Tovar-Sánchez & Gabriel Navarro',
        'journal': 'Remote Sensing',
        'journal_logo': 'remsens_logo.png',
        'image': 'mosaicking.PNG',
        'date': '2024 - Remote Sensing',
        'doi': 'https://doi.org/10.3390/rs16020290',
        'pdf': 'https://www.mdpi.com/2072-4292/16/2/290.pdf'
    },
    {
        'title': 'Characterization of an antarctic penguin colony ecosystem using high-resolution UAV hyperspectral imagery',
        'authors': '<strong>Alejandro Román</strong>, Antonio Tovar-Sánchez, Beatriz Fernández-Marín, Gabriel Navarro & Luis Barbero',
        'journal': 'International Journal of Applied Earth Observation and Geoinformation',
        'journal_logo': 'jag_logo.png',
        'image': 'hannahpoint.PNG',
        'date': '2023 - Int. Journal of Applied Earth Observation and Geoinformation',
        'doi': 'https://doi.org/10.1016/j.jag.2023.103565',
        'pdf': 'https://www.sciencedirect.com/science/article/pii/S1569843223003898/pdf'
    },
    {
        'title': 'Mapping intertidal oyster farms using unmanned aerial vehicles (UAV) high-resolution multispectral data',
        'authors': '<strong>Alejandro Román</strong>, Hermansyah Prasyad, Simon Oiry, Bede F.R. Davies, Guillaume Brunier & Laurent Barillé',
        'journal': 'Estuarine, Coastal and Shelf Science',
        'journal_logo': 'shelf_logo.png',
        'image': 'oysters.PNG',
        'date': '2023 - Estuarine, Coastal and Shelf Science',
        'doi': 'https://doi.org/10.1016/j.ecss.2023.108432',
        'pdf': 'https://www.sciencedirect.com/science/article/pii/S0272771423002226/pdf'
    },
    {
        'title': 'Water-Quality Monitoring with a UAV-Mounted Multispectral Camera in Coastal Waters',
        'authors': '<strong>Alejandro Román</strong>, Antonio Tovar-Sánchez, Adam Gauci, Alan Deidun, Isabel Caballero, Emanuele Colica, Sebastiano D\'Amico & Gabriel Navarro',
        'journal': 'Remote Sensing',
        'journal_logo': 'remsens_logo.png',
        'image': 'malta.PNG',
        'date': '2023 - Remote Sensing',
        'doi': 'https://doi.org/10.3390/rs15010237',
        'pdf': 'https://www.mdpi.com/2072-4292/15/1/237.pdf'
    },
    {
        'title': 'Remote Sensing: Satellite and RPAS (Remotely Piloted Aircraft System)',
        'authors': 'Martha Bonnet Dunbar, Isabel Caballero, <strong>Alejandro Román</strong> & Gabriel Navarro',
        'journal': 'Springer',
        'journal_logo': 'springer_logo.png',
        'image': 'dunbar.PNG',
        'date': '2022 - Springer',
        'doi': 'https://doi.org/10.1007/978-3-031-14486-8_9',
        'pdf': 'https://doi.org/10.1007/978-3-031-14486-8_9'
    },
    {
        'title': 'Monitoring the marine invasive alien species Rugulopteryx okamurae using unmanned aerial vehicles and satellites',
        'authors': 'Mar Roca, Martha Bonnet Dunbar, <strong>Alejandro Román</strong>, Isabel Caballero, Maria Laura Zoffoli, Pierre Gernez & Gabriel Navarro',
        'journal': 'Frontiers in Marine Science',
        'journal_logo': 'fmar_logo.png',
        'image': 'roca.png',
        'date': '2022 - Frontiers in Marine Science',
        'doi': 'https://doi.org/10.3389/fmars.2022.1004012',
        'pdf': 'https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.1004012/pdf'
    },
    {
        'title': 'High-spatial resolution UAV multispectral data complementing satellite imagery to characterize a chinstrap penguin colony ecosystem on deception island (Antarctica)',
        'authors': '<strong>Alejandro Román</strong>, Gabriel Navarro, Isabel Caballero & Antonio Tovar-Sánchez',
        'journal': 'GIScience & Remote Sensing',
        'journal_logo': 'gisci_logo.png',
        'image': 'gisci.PNG',
        'date': '2022 - GIScience & Remote Sensing',
        'doi': 'https://doi.org/10.1080/15481603.2022.2101702',
        'pdf': 'https://www.tandfonline.com/doi/epdf/10.1080/15481603.2022.2101702?needAccess=true'
    },
    {
        'title': 'Unmanned aerial vehicles (UAVs) as a tool for hazard assessment: The 2021 eruption of Cumbre Vieja volcano, La Palma Island (Spain)',
        'authors': '<strong>Alejandro Román</strong>, Antonio Tovar-Sánchez, David Roque-Atienza, I.Emma Huertas, Isabel Caballero, Eugenio Fraile-Nuez & Gabriel Navarro',
        'journal': 'Science of The Total Environment',
        'journal_logo': 'stoten_logo.png',
        'image': 'palma_drones.PNG',
        'date': '2022 - Science of The Total Environment',
        'doi': 'https://doi.org/10.1016/j.scitotenv.2022.157092',
        'pdf': 'https://www.sciencedirect.com/science/article/pii/S0048969722041894/pdf'
    },
    {
        'title': 'Water quality monitoring with Sentinel-2 and Landsat-8 satellites during the 2021 volcanic eruption in La Palma (Canary Islands)',
        'authors': 'Isabel Caballero, <strong>Alejandro Román</strong>, Antonio Tovar-Sánchez & Gabriel Navarro',
        'journal': 'Science of The Total Environment',
        'journal_logo': 'stoten_logo.png',
        'image': 'palma_sat.PNG',
        'date': '2022 - Science of The Total Environment',
        'doi': 'https://doi.org/10.1016/j.scitotenv.2022.153433',
        'pdf': 'https://www.sciencedirect.com/science/article/pii/S0048969722005253/pdf'
    },
    {
        'title': 'Applications of unmanned aerial vehicles in Antarctic environmental research',
        'authors': 'Antonio Tovar‑Sánchez, <strong>Alejandro Román</strong>, David Roque‑Atienza & Gabriel Navarro',
        'journal': 'Scientific Reports',
        'journal_logo': 'scirep_logo.png',
        'image': 'tovar.png',
        'date': '2021 - Scientific Reports',
        'doi': 'https://doi.org/10.1038/s41598-021-01228-z',
        'pdf': 'https://www.nature.com/articles/s41598-021-01228-z.pdf'
    },
    {
        'title': 'Using a UAV-Mounted Multispectral Camera for the Monitoring of Marine Macrophytes',
        'authors': '<strong>Alejandro Román</strong>, Antonio Tovar-Sánchez, Irene Olivé & Gabriel Navarro',
        'journal': 'Frontiers in Marine Science',
        'journal_logo': 'fmar_logo.png',
        'image': 'santi.png',
        'date': '2021 - Frontiers in Marine Science',
        'doi': 'https://doi.org/10.3389/fmars.2021.722698',
        'pdf': 'https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2021.722698/pdf'
    }
]

# Media data
MEDIA_ITEMS = [
    {
        'title': 'Un Punto Azul Podcast',
        'description': 'Participation in the Un Punto Azul podcast. Introduction to the talk Observing the Poles in Drone Mode, which will take place next Monday, May 18, at Pint of Science.',
        'image': 'puntoazul.png',
        'url': 'https://www.youtube.com/watch?v=TQ_zDnm0TiE&list=PLpGYDZSZzihSMIkhdECjoah56GNljq5pZ',
        'date': '5 May 2026',
        'tags': []
    },
    {
        'title': 'Canal Sur Radio - Interview on the program Cambio Climático',
        'description': 'Interview on the program Climate Change on Canal Sur Radio, stating that red snow algae are more widespread than previously known in the planet\'s frozen regions (from minute 34:50).',
        'image': 'climatechange.png',
        'url': 'https://www.canalsur.es/radio/programas/cambio-climatico/',
        'date': '20 March 2026',
        'tags': []
    },
    {
        'title': 'Onda Cádiz - Interview on the program El Mirador',
        'description': 'Dr. Alejandro Román was interviewed about his publication on red snow algal blooms in Antarctica and their relationship with climate change.',
        'image': 'snowalgaenew.png',
        'url': 'https://www.youtube.com/watch?v=eZS7aQ_L8JA',
        'date': '11 March 2026',
        'tags': []
    },
    {
        'title': 'Canal Sur TV - 28F Global',
        'description': 'Interview featured in the Canal Sur TV special 28F Global, in which Dr. Alejandro Román discusses daily life and research projects carried out during the 2026 Spanish Antarctic Campaign.',
        'image': '28f.png',
        'url': 'https://www.canalsurmas.es/videos/detail/327967-andalucia-global-27f-b4-20260228',
        'date': '28 February 2026',
        'tags': []
    },
    {
        'title': 'Press Release - The Extent of Algae Turning Antarctic Snow Pink Is Greater Than Expected',
        'description': 'The algae responsible for the "pink snow" phenomenon, which covers large areas in Antarctic regions, are proliferating due to climate change and, in turn, accelerating it by enhancing ice melt.',
        'image': '22012026.png',
        'url': 'https://www.csic.es/es/actualidad-del-csic/la-extension-de-las-algas-que-tinen-de-rosa-la-nieve-de-la-antartida-es-mayor-de-lo-esperado',
        'date': '22 January 2026',
        'tags': []
    },
    {
        'title': 'YouTube - Science to Reduce the Environmental Impact of Sunscreens on Our Coasts',
        'description': 'Interview by Ana Lozano del Campo about the Turisdron project, in which drone-mounted sensors were used to analyze the impact of UV filters on water quality and marine ecosystems.',
        'image': 'cremas.png',
        'url': 'https://www.youtube.com/watch?v=G5KdS79gE9U&t=3s',
        'date': '28 October 2025',
        'tags': []
    },
    {
        'title': 'À Punt Radiotelevisió Valenciana - News Interview',
        'description': 'Dr. Alejandro Román explains how drone technology made it possible to assess the environmental impact of the 2024 cut-off low (DANA) event in Valencia.',
        'image': 'apunt.png',
        'url': 'https://www.linkedin.com/posts/instituto-de-ciencias-marinas-de-andaluc%C3%ADa-icman-csic_icman-csic-drones-ugcPost-7384565695172460544-5DAd?utm_source=share&utm_medium=member_desktop&rcm=ACoAAC5cnNQBd0TMM84YZLSXRCmjF5ACQ8I5ASI',
        'date': '16 October 2025',
        'tags': []
    },
    {
        'title': 'Press Release - CSIC Study Highlights the Role of Drones in Assessing Infrastructure and Pollutants During the 2024 DANA Event',
        'description': 'In the days following the floods in Valencia, CSIC scientific and technical staff conducted around twenty flights using unmanned aerial vehicles to evaluate environmental impacts and infrastructure damage.',
        'image': '15102025.png',
        'url': 'https://www.csic.es/es/actualidad-del-csic/un-estudio-del-csic-destaca-la-aportacion-de-los-drones-en-la-evaluacion-de-infraestructuras-y-contaminantes-en-la-dana-de-2024',
        'date': '15 October 2025',
        'tags': []
    },
    {
        'title': 'Canal Sur TV - Espacio Protegido: Recovery of Disused Salt Marshes, Key to Reducing Greenhouse Gases',
        'description': 'Report on a study led by Silvia Amaya in the Bay of Cádiz. Dr. Alejandro Román contributed by using drones to carry out high-resolution monitoring of the extent of different salt marshes in the area.',
        'image': 'salinas.png',
        'url': 'https://www.canalsur.es/television/programas/espacio-protegido/noticia/2196383.html',
        'date': '14 September 2025',
        'tags': []
    },
    {
        'title': 'El Confidencial - The Asian Alga Devastating Cádiz Reaches Cantabria',
        'description': 'Press interview in which Drs. Gabriel Navarro and Alejandro Román share their insights on this environmentally significant phenomenon affecting the province of Cádiz.',
        'image': 'okamurae.png',
        'url': 'https://www.elconfidencial.com/espana/2025-08-26/alga-especie-invasora-cantabria-cadiz-mar-asiatica_4196464/',
        'date': '26 August 2025',
        'tags': []
    },
    {
        'title': 'Onda Cádiz - Program El Mirador',
        'description': 'Interview with Dr. Alejandro Román discussing the development of his research projects, also in the context of the 70th anniversary of ICMAN-CSIC.',
        'image': 'mirador.png',
        'url': 'https://ondacadiz.es/programa-television/el-mirador-info/2025/el-mirador-info-148',
        'date': '14 August 2025',
        'tags': []
    },
    {
        'title': 'Fulbright Spain - Interview with 2024 Predoctoral Fulbright Fellows',
        'description': 'Alejandro Román takes part in an interview for Fulbright Spain, sharing his full experience in the United States, including how it has shaped his personal and professional life.',
        'image': 'fulbright2.png',
        'url': 'https://www.youtube.com/watch?v=y_P2jvU3tBM',
        'date': '24 September 2024',
        'tags': []
    },
    {
        'title': 'CSIC Investiga - Oceans: The Future of Marine Science Facing the Challenges of Global Change',
        'description': 'Publication in the latest issue of CSIC Investiga ("Oceans"), in which Alejandro Román explains how his PhD research contributes to addressing major global change challenges.',
        'image': 'oceanos.png',
        'url': 'https://digital.csic.es/handle/10261/359768',
        'date': '01 June 2024',
        'tags': []
    },
    {
        'title': 'BBVA OpenMind - Monitoring Antarctica from a Drone\'s-Eye View',
        'description': 'Interview by Elena S. García discussing Antarctic polar research in the context of climate change, the Fulbright experience in the United States, and general reflections on the PhD journey.',
        'image': 'bbva_openmind.png',
        'url': 'https://www.bbvaopenmind.com/ciencia/medioambiente/alejandro-roman-oceanografo-monitoriza-ecosistema-antartico-vista-dron/',
        'date': '23 April 2024',
        'tags': []
    },
    {
        'title': 'RNE Program Españoles en la Mar - A New Georeferencing and Mosaicking Algorithm',
        'description': 'Interview presenting a new georeferencing and mosaicking algorithm for drone imagery collected over water-covered surfaces. The interview can be heard starting at 18:01 (-17:05).',
        'image': 'mosaic.png',
        'url': 'https://www.rtve.es/play/audios/espanoles-en-la-mar/espanoles-mar-reivindicaciones-pesquero-26f/15985631/',
        'date': '23 February 2024',
        'tags': []
    },
    {
        'title': 'Press Release - CSIC Publishes the First Open Repository of Photogrammetric Data Captured by Drones in Antarctica',
        'description': 'The study provides a highly valuable source of information for both national and international research, given the difficulty of accessing these remote regions.',
        'image': '23022024.png',
        'url': 'https://www.csic.es/es/actualidad-del-csic/el-csic-publica-en-abierto-el-primer-repositorio-de-datos-fotogrametricos-capturados-con-drones-en-la-antartida',
        'date': '23 February 2024',
        'tags': []
    },
    {
        'title': 'Fulbright Spain Blog - "Droning" on the Other Side of the Atlantic: A Once-in-a-Lifetime Fulbright Experience',
        'description': 'A short piece summarizing the experiences, emotions, and key moments of my Fulbright stay at the University of Maryland Center for Environmental Science (UMCES).',
        'image': 'fulbright.png',
        'url': 'https://blog.fulbright.es/droneando-al-otro-lado-del-atlantico-una-experiencia-fulbright-para-toda-la-vida/',
        'date': '21 February 2024',
        'tags': []
    },
    {
        'title': 'Press Release - CSIC Develops Software to Study Aquatic Ecosystems',
        'description': 'The software enables advanced analysis and monitoring of aquatic environments using innovative technological approaches.',
        'image': '22012024.png',
        'url': 'https://www.csic.es/es/actualidad-del-csic/el-csic-desarrolla-un-software-para-estudiar-los-ecosistemas-acuaticos',
        'date': '22 January 2024',
        'tags': []
    },
    {
        'title': 'UMCES Website - Meet Visiting Fulbright Scholar Alejandro Román',
        'description': 'Interview about the development of Alejandro Román\'s Fulbright project at the Horn Point Laboratory (UMCES).',
        'image': 'umces.png',
        'url': 'https://www.umces.edu/news/meet-visiting-fulbright-scholar-alejandro-roman',
        'date': '2 November 2023',
        'tags': []
    },
    {
        'title': 'Smithsonian Website - Remote (Controlled)',
        'description': 'An interesting article by Mark Piesing on the use of drones in Antarctic polar research, including the PiMetAn project.',
        'image': 'smith.png',
        'url': 'https://airandspace.si.edu/air-and-space-quarterly/fall-2022/remote-controlled',
        'date': '21 September 2022',
        'tags': []
    },
    {
        'title': 'Canal Sur Radio - Interview on the program Canal Sur Mediodía Cádiz',
        'description': 'Interview about the PiMetAn polar project, featuring researchers Erica Sparaventi and Alejandro Román. The interview starts at minute 29:35 of the June 3rd, 2021 broadcast.',
        'image': 'canalsur.png',
        'url': 'https://www.canalsur.es/radio/programas/cadiz-mediodia/detalle/2894647.html?video=2065580',
        'date': '03 June 2021',
        'tags': []
    }
]

# Category mapping for media items
_MEDIA_CATEGORIES = [
    'Podcast', 'Radio', 'TV', 'TV', 'Press',
    'Video', 'TV', 'Press', 'TV', 'Press',
    'TV', 'Video', 'Article', 'Article', 'Radio',
    'Press', 'Article', 'Press', 'Article', 'Article', 'Radio'
]
for _i, _cat in enumerate(_MEDIA_CATEGORIES):
    MEDIA_ITEMS[_i]['category'] = _cat

# Category mapping for publications
_PUB_CATEGORIES = [
    'Polar', 'Emergencies', 'Polar', 'Coastal Ecology', 'Coastal Ecology',
    'AI', 'Coastal Ecology', 'Coastal Ecology', 'Polar', 'Ocean Color',
    'Polar', 'Coastal Ecology', 'Ocean Color', 'Ocean Color', 'Coastal Ecology',
    'Polar', 'Emergencies', 'Emergencies', 'Polar', 'Coastal Ecology'
]
for _i, _cat in enumerate(_PUB_CATEGORIES):
    PUBLICATIONS[_i]['category'] = _cat

def clean_output_dir():
    """Remove and recreate the output directory"""
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(exist_ok=True)

def copy_static_files():
    """Copy static files (CSS, JS, images) to output directory"""
    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, OUTPUT_DIR / 'static', dirs_exist_ok=True)

def render_template(template_name, output_path, **context):
    """Render a Jinja2 template and save to output path"""
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template(template_name)

    # Add site config to context
    context['site'] = SITE_CONFIG

    html = template.render(**context)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generated: {output_path}")

def generate_site():
    """Generate the complete static site"""
    print("Building Alejandro Román's Website...")
    print("-" * 50)

    # Clean and prepare output directory
    clean_output_dir()

    # Copy static files
    copy_static_files()

    # Generate pages
    render_template('index.html', OUTPUT_DIR / 'index.html', page='home')
    render_template('about.html', OUTPUT_DIR / 'about.html', page='about')
    render_template('team.html', OUTPUT_DIR / 'team.html', page='team')
    render_template('publications.html', OUTPUT_DIR / 'publications.html',
                   page='publications', publications=PUBLICATIONS)
    render_template('amiga.html', OUTPUT_DIR / 'amiga.html', page='amiga')
    render_template('abanti.html', OUTPUT_DIR / 'abanti.html', page='abanti')
    render_template('media.html', OUTPUT_DIR / 'media.html',
                   page='media', media_items=MEDIA_ITEMS)

    # Copy .nojekyll for GitHub Pages
    (OUTPUT_DIR / '.nojekyll').touch()

    print("-" * 50)
    print("Build complete! Site generated in 'docs/' directory")
    print("You can now commit and push to GitHub for deployment")

if __name__ == '__main__':
    generate_site()
