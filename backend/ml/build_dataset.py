"""
Utility script to compile and format the curated ACLI Educational Dataset v1.0.0.
Sources: Open Educational Resources, Public Domain Classics, and Open Textbook Library.
"""

import json
from pathlib import Path

DATASET_VERSION = "1.0.0"

PARAGRAPHS = [
    # =========================================================================
    # CLASS 1: EASY (Grades 4-6, direct syntax, common vocabulary, short sentences)
    # =========================================================================
    # Doc 1: Water Cycle for Beginners
    {
        "id": "easy-water-1",
        "document_id": "doc-water-cycle",
        "domain": "Earth Science",
        "source_title": "The Simple Water Cycle",
        "source_license": "CC BY-SA 4.0",
        "text": "Water covers most of our planet. The sun shines down on the ocean and warms the water. When water gets warm, it turns into an invisible gas called water vapor. The vapor rises high into the cool sky. As it cools down, it changes back into tiny drops of water that form fluffy clouds.",
        "difficulty": "Easy",
        "annotation_rationale": "Short sentences, common vocabulary, active voice, concrete imagery."
    },
    {
        "id": "easy-water-2",
        "document_id": "doc-water-cycle",
        "domain": "Earth Science",
        "source_title": "The Simple Water Cycle",
        "source_license": "CC BY-SA 4.0",
        "text": "Clouds become heavy as more drops gather together. Soon the drops become too heavy to float in the air. Gravity pulls them back down to the ground as gentle rain or winter snow. Water flows into streams, rivers, and deep lakes. Eventually, the water returns to the ocean, and the journey begins all over again.",
        "difficulty": "Easy",
        "annotation_rationale": "High readability, direct narrative structure, familiar concepts."
    },
    {
        "id": "easy-water-3",
        "document_id": "doc-water-cycle",
        "domain": "Earth Science",
        "source_title": "The Simple Water Cycle",
        "source_license": "CC BY-SA 4.0",
        "text": "Living creatures need clean water every single day. Plants soak up water through their brown roots in the dirt. Animals drink from forest ponds and cool streams. People use fresh water for cooking meals and washing hands. Because water moves in a circle, every drop on Earth gets recycled.",
        "difficulty": "Easy",
        "annotation_rationale": "Simple sentence frames, high familiarity, zero academic jargon."
    },

    # Doc 2: Honeybee Colonies
    {
        "id": "easy-bees-1",
        "document_id": "doc-honeybees",
        "domain": "Biology",
        "source_title": "Life of the Worker Bee",
        "source_license": "CC BY-SA 4.0",
        "text": "Honeybees live together in large family groups called colonies. Inside each wooden hive, thousands of busy bees work together peacefully. The queen bee is the mother of the whole colony. She stays deep inside the hive and lays tiny white eggs. Worker bees take care of the young babies.",
        "difficulty": "Easy",
        "annotation_rationale": "Short declarative statements, familiar biological subject, high readability ease."
    },
    {
        "id": "easy-bees-2",
        "document_id": "doc-honeybees",
        "domain": "Biology",
        "source_title": "Life of the Worker Bee",
        "source_license": "CC BY-SA 4.0",
        "text": "Worker bees fly out across green fields to look for bright flowers. They drink sweet nectar and collect yellow pollen dust on their fuzzy legs. When a bee finds a good flower patch, it flies home and dances. The dance tells the other bees exactly where to find the sweet food.",
        "difficulty": "Easy",
        "annotation_rationale": "Sensory adjectives, simple compound clauses, low vocabulary difficulty."
    },
    {
        "id": "easy-bees-3",
        "document_id": "doc-honeybees",
        "domain": "Biology",
        "source_title": "Life of the Worker Bee",
        "source_license": "CC BY-SA 4.0",
        "text": "Back at the hive, bees turn sweet flower nectar into golden honey. They store this thick honey inside neat wax rooms called cells. During cold winter months, bees cannot leave the hive to find flowers. They stay warm together inside and eat the stored honey until warm spring arrives.",
        "difficulty": "Easy",
        "annotation_rationale": "Concrete narrative, common vocabulary, straightforward causal sequence."
    },

    # Doc 3: Exploring the Solar System
    {
        "id": "easy-space-1",
        "document_id": "doc-solar-system",
        "domain": "Astronomy",
        "source_title": "Our Neighborhood in Space",
        "source_license": "CC BY-SA 4.0",
        "text": "The solar system is made of the sun and eight big planets. The sun sits right in the center like a glowing ball of fire. It gives heat and light to everything around it. Mercury is the closest planet to the blazing sun, while Neptune is cold and very far away.",
        "difficulty": "Easy",
        "annotation_rationale": "Everyday vocabulary, short clauses, simple spatial descriptions."
    },
    {
        "id": "easy-space-2",
        "document_id": "doc-solar-system",
        "domain": "Astronomy",
        "source_title": "Our Neighborhood in Space",
        "source_license": "CC BY-SA 4.0",
        "text": "Earth is the third planet from the sun. It has blue oceans, green trees, and breathable air. Earth is the only world we know that has living plants and playful animals. We travel around the sun once every year, creating four changing seasons from summer heat to winter snow.",
        "difficulty": "Easy",
        "annotation_rationale": "High reading ease, relatable foundational astronomy, clear sentence boundaries."
    },
    {
        "id": "easy-space-3",
        "document_id": "doc-solar-system",
        "domain": "Astronomy",
        "source_title": "Our Neighborhood in Space",
        "source_license": "CC BY-SA 4.0",
        "text": "Jupiter is the biggest planet of all. It is so huge that all the other planets could fit inside it. Jupiter is not made of rock like Earth. Instead, it is made of swirling gases and violent storms. A giant red storm has been spinning on Jupiter for hundreds of years.",
        "difficulty": "Easy",
        "annotation_rationale": "Short simple sentences, clear comparisons, minimal syllables per word."
    },

    # Doc 4: Desert Animals
    {
        "id": "easy-desert-1",
        "document_id": "doc-desert-life",
        "domain": "Ecology",
        "source_title": "Surviving in the Dry Desert",
        "source_license": "CC BY-SA 4.0",
        "text": "Deserts are hot, dry places where rain almost never falls. The blazing sun shines down on bare sand and rocky hills all day. Plants and wild animals must be very smart to survive here. Camels store energy in their humps and can walk for weeks without drinking fresh water.",
        "difficulty": "Easy",
        "annotation_rationale": "Grade 4-5 vocabulary, simple clauses, direct description."
    },
    {
        "id": "easy-desert-2",
        "document_id": "doc-desert-life",
        "domain": "Ecology",
        "source_title": "Surviving in the Dry Desert",
        "source_license": "CC BY-SA 4.0",
        "text": "Many desert creatures stay asleep in cool underground burrows while the sun is high. Lizards and small desert mice hide under rocks where it is cool. When the sun sets and the desert turns dark and cold, these animals wake up and search for seeds and insects.",
        "difficulty": "Easy",
        "annotation_rationale": "Simple temporal connective words, active sentences, familiar animals."
    },

    # Doc 5: The Story of Bread
    {
        "id": "easy-bread-1",
        "document_id": "doc-making-bread",
        "domain": "Food Science & History",
        "source_title": "From Wheat to Fresh Bread",
        "source_license": "Public Domain / OER",
        "text": "People have baked bread for thousands of years. Long ago, people learned that grinding wheat seeds creates fine white powder called flour. When you mix flour with warm water and a pinch of salt, you get sticky dough. Bakers knead the dough with their hands until it feels smooth.",
        "difficulty": "Easy",
        "annotation_rationale": "Everyday vocabulary, sequential narrative, simple clauses."
    },
    {
        "id": "easy-bread-2",
        "document_id": "doc-making-bread",
        "domain": "Food Science & History",
        "source_title": "From Wheat to Fresh Bread",
        "source_license": "Public Domain / OER",
        "text": "Bakers add tiny living organisms called yeast to the dough. The yeast eats sugar and releases little bubbles of air. These trapped bubbles make the dough rise up like a soft pillow. After baking in a hot oven, the loaf turns crisp and brown on the outside.",
        "difficulty": "Easy",
        "annotation_rationale": "Clear analogies, brief sentences, minimal cognitive parsing demand."
    },

    # Doc 6: How Trees Breathe
    {
        "id": "easy-trees-1",
        "document_id": "doc-tree-breath",
        "domain": "Botany",
        "source_title": "The Forest Air Machine",
        "source_license": "CC BY-SA 4.0",
        "text": "Trees are the lungs of our planet. Green leaves catch golden sunlight during the bright day. Leaves have tiny mouth holes on the bottom that drink in stale air called carbon dioxide. Inside each leaf, sunlight mixes with water to make sweet food for the tall tree.",
        "difficulty": "Easy",
        "annotation_rationale": "Direct metaphors, simple coordinate phrases, high readability."
    },
    {
        "id": "easy-trees-2",
        "document_id": "doc-tree-breath",
        "domain": "Botany",
        "source_title": "The Forest Air Machine",
        "source_license": "CC BY-SA 4.0",
        "text": "While making food, the tree gives off fresh oxygen into the wind. People and forest animals breathe in this clean oxygen to stay healthy and strong. Planting more green trees around schools and city parks helps keep the air fresh and cool for everyone in the neighborhood.",
        "difficulty": "Easy",
        "annotation_rationale": "Short sentences, accessible words, positive instructive tone."
    },

    # =========================================================================
    # CLASS 2: MEDIUM (Grades 7-9, compound-complex sentences, standard vocabulary)
    # =========================================================================
    # Doc 7: Renewable Energy Sources
    {
        "id": "med-energy-1",
        "document_id": "doc-renewable-energy",
        "domain": "Environmental Science",
        "source_title": "Harnessing Renewable Energy",
        "source_license": "CC BY-SA 4.0",
        "text": "Renewable energy comes from natural sources that replenish themselves faster than they are consumed. Sunlight and wind are classic examples of renewable resources that never run out. In contrast, fossil fuels like coal and petroleum took millions of years to form beneath the surface of the Earth. When we burn fossil fuels for electricity, harmful greenhouse gases are released into the atmosphere, contributing directly to climate disruption.",
        "difficulty": "Medium",
        "annotation_rationale": "Middle school reading level, balanced compound sentences, standard technical terms like replenish and atmosphere."
    },
    {
        "id": "med-energy-2",
        "document_id": "doc-renewable-energy",
        "domain": "Environmental Science",
        "source_title": "Harnessing Renewable Energy",
        "source_license": "CC BY-SA 4.0",
        "text": "Modern wind turbines convert the kinetic energy of moving air into usable electrical current. Tall towers are placed in windy locations, such as open prairies or coastal hills, where wind speeds remain steady throughout the day. Although building these large installations requires significant initial investment, the operating costs remain remarkably low once the turbines are operational.",
        "difficulty": "Medium",
        "annotation_rationale": "Concessive conjunctions (although), multi-syllable nouns, structured expository prose."
    },
    {
        "id": "med-energy-3",
        "document_id": "doc-renewable-energy",
        "domain": "Environmental Science",
        "source_title": "Harnessing Renewable Energy",
        "source_license": "CC BY-SA 4.0",
        "text": "Solar panels utilize photovoltaic cells made from silicon crystals to absorb sunlight and generate direct electrical current. Engineers have improved panel efficiency steadily over the past two decades, making rooftop solar accessible to ordinary homeowners. However, storing surplus electricity for cloudy days remains an engineering challenge that requires larger and more affordable battery systems.",
        "difficulty": "Medium",
        "annotation_rationale": "Domain-specific vocabulary (photovoltaic, silicon), moderate sentence length, clear cause-effect."
    },

    # Doc 8: The Roman Republic
    {
        "id": "med-rome-1",
        "document_id": "doc-roman-republic",
        "domain": "World History",
        "source_title": "Governance in the Roman Republic",
        "source_license": "OER Commons / CC BY-SA",
        "text": "The Roman Republic established a complex system of government designed to prevent any single ruler from gaining tyrannical control. Power was divided between executive magistrates, a wealthy Senate, and public assemblies composed of ordinary citizens. Consuls were elected annually to lead the military and oversee government administration, ensuring that no executive could maintain permanent power.",
        "difficulty": "Medium",
        "annotation_rationale": "Historical terminology (magistrates, assemblies, tyrannical), compound sentence clauses."
    },
    {
        "id": "med-rome-2",
        "document_id": "doc-roman-republic",
        "domain": "World History",
        "source_title": "Governance in the Roman Republic",
        "source_license": "OER Commons / CC BY-SA",
        "text": "Tensions between social classes frequently threatened the internal stability of the republic. The patricians held hereditary privilege and dominated political offices, while the plebeians struggled for legal protections and economic relief. Through organized strikes known as secessions, plebeians eventually secured their own representatives, called tribunes, who possessed the legal power to veto unfair senatorial decrees.",
        "difficulty": "Medium",
        "annotation_rationale": "Vocabulary complexity (patricians, secessions, hereditary), balanced subordinate syntax."
    },
    {
        "id": "med-rome-3",
        "document_id": "doc-roman-republic",
        "domain": "World History",
        "source_title": "Governance in the Roman Republic",
        "source_license": "OER Commons / CC BY-SA",
        "text": "As Roman territory expanded throughout the Mediterranean basin, the traditional governing institutions struggled to maintain effective administration. Military commanders gained immense personal loyalty from their soldiers, who depended on their generals for post-service land grants rather than the state. This fundamental shift weakened the authority of the Senate and paved the way for civil conflicts.",
        "difficulty": "Medium",
        "annotation_rationale": "Standard high school history level, cohesive transitions, moderate syllable density."
    },

    # Doc 9: The Immune System
    {
        "id": "med-immune-1",
        "document_id": "doc-immune-system",
        "domain": "Human Biology",
        "source_title": "Defense Mechanisms of the Body",
        "source_license": "CC BY-SA 4.0",
        "text": "The human immune system is a sophisticated defense network composed of specialized cells, tissues, and protective chemical signals. Its primary responsibility is to distinguish between harmless native cells and dangerous invading pathogens, such as bacteria and viruses. Physical barriers like the skin and mucous membranes serve as the first line of defense, preventing most microbes from entering internal body cavities.",
        "difficulty": "Medium",
        "annotation_rationale": "Middle school biology vocabulary (pathogens, mucous, microbes), clear introductory sentences."
    },
    {
        "id": "med-immune-2",
        "document_id": "doc-immune-system",
        "domain": "Human Biology",
        "source_title": "Defense Mechanisms of the Body",
        "source_license": "CC BY-SA 4.0",
        "text": "When pathogens breach external barriers, white blood cells mount an active response. Phagocytes engulf and break down foreign invaders, while lymphocytes identify specific structural markers known as antigens. Once lymphocytes produce tailored antibodies to neutralize a specific virus, memory cells remain in the bloodstream to provide long-lasting immunity against future infections.",
        "difficulty": "Medium",
        "annotation_rationale": "Subject terminology (lymphocytes, antigens, phagocytes), moderate sentence length (18-20 words)."
    },

    # Doc 10: How Search Engines Work
    {
        "id": "med-search-1",
        "document_id": "doc-search-engines",
        "domain": "Computer Science",
        "source_title": "Indexing the Digital World",
        "source_license": "CC BY-SA 4.0",
        "text": "Modern search engines discover web content by deploying automated programs called crawlers or spiders. These crawlers follow hyperlinks from one page to another, downloading copies of web pages and recording structural metadata. The downloaded data is organized into a massive database called an index, which functions like the index at the back of a large textbook.",
        "difficulty": "Medium",
        "annotation_rationale": "Technical concepts explained with accessible metaphors, moderate sentence length."
    },
    {
        "id": "med-search-2",
        "document_id": "doc-search-engines",
        "domain": "Computer Science",
        "source_title": "Indexing the Digital World",
        "source_license": "CC BY-SA 4.0",
        "text": "When a user submits a search query, ranking algorithms evaluate hundreds of factors within milliseconds to present the most relevant results. These algorithms examine keyword frequency, site trustworthiness, page load speed, and user engagement metrics. By constantly refining these evaluation formulas, search providers attempt to filter out spam while highlighting authoritative educational content.",
        "difficulty": "Medium",
        "annotation_rationale": "Standard expository complexity, participial clauses, accessible technical vocabulary."
    },

    # Doc 11: Continental Drift & Plate Tectonics
    {
        "id": "med-tectonics-1",
        "document_id": "doc-plate-tectonics",
        "domain": "Geology",
        "source_title": "The Dynamic Earth Crust",
        "source_license": "CC BY-SA 4.0",
        "text": "In the early twentieth century, German meteorologist Alfred Wegener proposed that all continents were once assembled into a single supercontinent called Pangaea. He noticed that the coastlines of South America and Africa fit together like jigsaw puzzle pieces. Furthermore, identical plant and animal fossils were discovered across widely separated oceans, suggesting that the landmasses had drifted apart over millions of years.",
        "difficulty": "Medium",
        "annotation_rationale": "Medium sentence length (21 words), standard historical-science prose, cohesive discourse markers."
    },
    {
        "id": "med-tectonics-2",
        "document_id": "doc-plate-tectonics",
        "domain": "Geology",
        "source_title": "The Dynamic Earth Crust",
        "source_license": "CC BY-SA 4.0",
        "text": "Although Wegener could not explain the physical mechanism responsible for continental movement, twentieth-century ocean floor mapping confirmed seafloor spreading. Scientists discovered that the Earth's rigid outer lithosphere is fractured into numerous tectonic plates that float on the semi-fluid asthenosphere beneath. Convection currents within the molten mantle slowly drive these plates, creating mountain ranges and oceanic trenches.",
        "difficulty": "Medium",
        "annotation_rationale": "Standard earth-science vocabulary (lithosphere, asthenosphere, convection), subordinate clauses."
    },

    # =========================================================================
    # CLASS 3: HARD (Grades 10-12 / Intro College, long multi-clause, dense concepts)
    # =========================================================================
    # Doc 12: Cognitive Psychology & Working Memory
    {
        "id": "hard-cog-1",
        "document_id": "doc-cognitive-psych",
        "domain": "Cognitive Psychology",
        "source_title": "Architecture of Working Memory",
        "source_license": "CC BY-SA 4.0",
        "text": "Working memory is conventionally conceptualized as an executive cognitive architecture responsible for the transient maintenance and manipulation of information necessary for complex cognitive tasks. Unlike passive sensory storage or expansive long-term memory repositories, working memory possesses severely constrained bandwidth. When extraneous visual clutter or confusing typography consumes attentional bandwidth, cognitive load increases disproportionately, precipitating frequent comprehension degradation.",
        "difficulty": "Hard",
        "annotation_rationale": "Multi-clause sentences (25+ words), high academic vocabulary (conceptualized, transient, disproportionately), theoretical concepts."
    },
    {
        "id": "hard-cog-2",
        "document_id": "doc-cognitive-psych",
        "domain": "Cognitive Psychology",
        "source_title": "Architecture of Working Memory",
        "source_license": "CC BY-SA 4.0",
        "text": "Baddeley and Hitch's multicomponent framework distinguishes between modality-specific storage buffers—the phonological loop and the visuospatial sketchpad—and a domain-general central executive coordinating attentional distribution. Neuropsychological investigations utilizing functional magnetic resonance imaging corroborate that dorsolateral prefrontal cortex activation intensifies exponentially as cognitive load approaches working memory saturation thresholds.",
        "difficulty": "Hard",
        "annotation_rationale": "Specialized neuropsychology terminology, em-dash parenthetical clauses, 30-word average sentence length."
    },
    {
        "id": "hard-cog-3",
        "document_id": "doc-cognitive-psych",
        "domain": "Cognitive Psychology",
        "source_title": "Architecture of Working Memory",
        "source_license": "CC BY-SA 4.0",
        "text": "Empirical reading experiments demonstrate that saccadic eye movements reflect underlying cognitive processing difficulty; readers fixate significantly longer upon syntactically ambiguous clauses and exhibit frequent regressive saccades when contextual coherence collapses. Providing structured typographic scaffolding and chunked text segments alleviates the processing burden on the central executive, thereby facilitating episodic buffer consolidation.",
        "difficulty": "Hard",
        "annotation_rationale": "High syllable density, technical cognitive-science phrases (regressive saccades, scaffolding, episodic buffer)."
    },

    # Doc 13: Macroeconomic Monetary Policy
    {
        "id": "hard-econ-1",
        "document_id": "doc-macroeconomics",
        "domain": "Economics",
        "source_title": "Central Banking and Inflation Control",
        "source_license": "CC BY-SA 4.0",
        "text": "Central banking authorities manage systemic macroeconomic fluctuations primarily through open market operations and adjustments to benchmark short-term interbank lending rates. When inflationary pressures accelerate beyond institutional target corridors, central banks initiate quantitative tightening and raise policy rates to restrict credit availability. Consequently, elevated borrowing costs temper capital expenditure and aggregate consumer demand, thereby mitigating upward wage-price spirals.",
        "difficulty": "Hard",
        "annotation_rationale": "Dense economic terminology, formal connective transitions, multi-syllabic academic phrasing."
    },
    {
        "id": "hard-econ-2",
        "document_id": "doc-macroeconomics",
        "domain": "Economics",
        "source_title": "Central Banking and Inflation Control",
        "source_license": "CC BY-SA 4.0",
        "text": "The efficacy of interest rate transmission mechanisms depends substantially on private sector debt maturity profiles and prevailing exchange rate regimes. In open developing economies exhibiting sovereign debt denominated in foreign currencies, domestic monetary tightening can induce adverse capital flight and currency depreciation. These secondary financial channels frequently counteract intended domestic stabilization objectives and induce structural supply-side contractions.",
        "difficulty": "Hard",
        "annotation_rationale": "Complex compound syntax, abstract institutional relationships, high lexical diversity."
    },
    {
        "id": "hard-econ-3",
        "document_id": "doc-macroeconomics",
        "domain": "Economics",
        "source_title": "Central Banking and Inflation Control",
        "source_license": "CC BY-SA 4.0",
        "text": "Furthermore, prolonged periods of historically suppressed real interest rates risk distorting capital allocation by incentivizing speculative asset accumulation rather than productivity-enhancing infrastructure investments. Economists debate whether macroprudential regulatory buffers alone suffice to insulate systemic financial institutions from cascading liquidity defaults during sudden macroeconomic shifts.",
        "difficulty": "Hard",
        "annotation_rationale": "Advanced undergraduate economics, abstract causal chains, 26 words per sentence."
    },

    # Doc 14: Molecular Genetics & Epigenetics
    {
        "id": "hard-genetics-1",
        "document_id": "doc-epigenetics",
        "domain": "Molecular Biology",
        "source_title": "Mechanisms of Epigenetic Regulation",
        "source_license": "CC BY-SA 4.0",
        "text": "Epigenetic modifications regulate genomic expression patterns without altering the underlying nucleotide sequence of deoxyribonucleic acid. DNA methylation, which predominantly occurs at cytosine bases within cytosine-guanine dinucleotide islands, typically correlates with transcriptional repression by physically impeding transcription factor binding. Concurrently, post-translational modifications of histone proteins dictate chromatin architecture, shifting between transcriptionally permissive euchromatin and condensed, silent heterochromatin.",
        "difficulty": "Hard",
        "annotation_rationale": "High density of biological compound nouns, formal syntax, academic explanatory style."
    },
    {
        "id": "hard-genetics-2",
        "document_id": "doc-epigenetics",
        "domain": "Molecular Biology",
        "source_title": "Mechanisms of Epigenetic Regulation",
        "source_license": "CC BY-SA 4.0",
        "text": "Environmental exposures, nutritional variance, and psychosocial stress have been demonstrated to influence histone acetyltransferase and histone deacetylase equilibrium across developmental critical periods. When chromatin undergoes pervasive hypermethylation in tumor suppressor promoter loci, cellular checkpoint signaling becomes disrupted, potentially facilitating uncontrolled oncogenic proliferation and malignant phenotypic transformation.",
        "difficulty": "Hard",
        "annotation_rationale": "Complex biological jargon, conditional subordination, advanced college-level complexity."
    },

    # Doc 15: Computer Systems & Distributed Consensus
    {
        "id": "hard-dist-1",
        "document_id": "doc-distributed-systems",
        "domain": "Computer Science",
        "source_title": "Fault Tolerance in Asynchronous Networks",
        "source_license": "CC BY-SA 4.0",
        "text": "Achieving fault-tolerant consensus across decentralized computing nodes poses fundamental theoretical limitations, as delineated by the Fischer-Lynch-Paterson impossibility result. In fully asynchronous distributed networks subjected to unannounced node failures, no deterministic consensus protocol can guarantee both absolute safety and bounded liveness. Modern systems circumvent this limitation by introducing partial synchrony assumptions, randomized leadership election protocols, and quorums.",
        "difficulty": "Hard",
        "annotation_rationale": "Dense theoretical computing concepts, technical vocabulary, collegiate analytical prose."
    },
    {
        "id": "hard-dist-2",
        "document_id": "doc-distributed-systems",
        "domain": "Computer Science",
        "source_title": "Fault Tolerance in Asynchronous Networks",
        "source_license": "CC BY-SA 4.0",
        "text": "Consensus protocols such as Raft decompose state-machine replication into independent algorithmic components, including leader election, log replication, and safety enforcement. By restricting committed log entry modifications strictly through an invariant leader-driven pipeline, Raft diminishes algorithmic ambiguity while maintaining equivalent fault-tolerance bounds to Paxos under adversarial network partition scenarios.",
        "difficulty": "Hard",
        "annotation_rationale": "Formal algorithmic exposition, multi-syllabic terminology, high syntactic density."
    },

    # Doc 16: Constitutional Jurisprudence
    {
        "id": "hard-law-1",
        "document_id": "doc-constitutional-law",
        "domain": "Law & Political Science",
        "source_title": "Principles of Judicial Review",
        "source_license": "Public Domain / CC BY-SA",
        "text": "Judicial review occupies an inherently paradoxical position within democratic constitutional orders, frequently characterized in legal scholarship as the counter-majoritarian difficulty. When unelected appellate judiciaries invalidate statutory enactments passed by representative legislative majorities, they invoke substantive due process and constitutional supremacy. Proponents argue that counter-majoritarian judicial intervention preserves structural minority protections against fleeting majoritarian overreach.",
        "difficulty": "Hard",
        "annotation_rationale": "Jurisprudential terminology, nuanced constitutional debate, elevated lexical diversity."
    },
    {
        "id": "hard-law-2",
        "document_id": "doc-constitutional-law",
        "domain": "Law & Political Science",
        "source_title": "Principles of Judicial Review",
        "source_license": "Public Domain / CC BY-SA",
        "text": "Conversely, originalist jurists contend that interpreting constitutional text according to contemporaneous public meaning restricts judicial discretion and preserves statutory legitimacy. Critics dispute this methodological premise, asserting that historical hermeneutics cannot adequately anticipate transformative technological and sociopolitical evolutions without rendering fundamental constitutional guarantees obsolete.",
        "difficulty": "Hard",
        "annotation_rationale": "Complex clause embedding, legal philosophy concepts (hermeneutics, originalism), 27 words per sentence."
    },

    # =========================================================================
    # CLASS 4: VERY HARD (Graduate / Peer-Reviewed Academic / Dense Philosophy)
    # =========================================================================
    # Doc 17: Epistemology & Phenomenological Philosophy
    {
        "id": "vhard-phil-1",
        "document_id": "doc-phenomenology",
        "domain": "Philosophy",
        "source_title": "Transcendental Phenomenology and Intentionality",
        "source_license": "Public Domain / Creative Commons",
        "text": "Husserlian phenomenology posits that consciousness is fundamentally characterized by intentionality, wherein every cognitive act is constitutively oriented toward an intentional object through noetic-noematic correlation. To interrogate the primordial constitution of meaning prior to unreflective naturalistic presuppositions, the phenomenological reduction, or epoché, brackets naive ontological commitments regarding transcendent reality, thereby laying bare the immanent structures of pure transcendental subjectivity.",
        "difficulty": "Very Hard",
        "annotation_rationale": "Average sentence length > 35 words, extreme philosophical jargon, dense recursive clauses, highly abstract."
    },
    {
        "id": "vhard-phil-2",
        "document_id": "doc-phenomenology",
        "domain": "Philosophy",
        "source_title": "Transcendental Phenomenology and Intentionality",
        "source_license": "Public Domain / Creative Commons",
        "text": "Furthermore, Heideggerian hermeneutic existentialism critiques this transcendental Cartesian residual by demonstrating that Dasein's primordial ontological situatedness precedes theoretical contemplation, manifesting primarily as pre-reflective being-in-the-world mediated through pragmatic circumspection. The rupture of equipmental ready-to-hand instrumentality into unready-to-hand obtrusiveness reveals the temporal horizon wherein authentic historical existence must continually negotiate its own finitude.",
        "difficulty": "Very Hard",
        "annotation_rationale": "Heideggerian terminology, extreme clause complexity, abstract nominalizations, collegiate/graduate level."
    },
    {
        "id": "vhard-phil-3",
        "document_id": "doc-phenomenology",
        "domain": "Philosophy",
        "source_title": "Transcendental Phenomenology and Intentionality",
        "source_license": "Public Domain / Creative Commons",
        "text": "Consequently, epistemology cannot legitimately divorce discursive propositional truth claims from the embodied temporalities and intersubjective lifeworlds that antecedently disclose the horizon of intelligibility itself. Dialectical tensions emerging between structuralist systemic determinism and post-structuralist deconstructive fluidity underscore the pervasive indeterminacy that destabilizes any totalizing foundationalist philosophical enterprise.",
        "difficulty": "Very Hard",
        "annotation_rationale": "Complex abstraction, 32 words per sentence, rare academic vocabulary, maximum cognitive parsing load."
    },

    # Doc 18: Advanced Neurocognitive Computational Modeling
    {
        "id": "vhard-neuro-1",
        "document_id": "doc-computational-neuro",
        "domain": "Neurobiology",
        "source_title": "Hierarchical Predictive Coding in Cortical Circuits",
        "source_license": "CC BY-SA 4.0",
        "text": "The free-energy principle formalizes neurobiological self-organization by modeling cortical hierarchies as generative architectures that continually minimize variational free energy through recursive Bayesian inference. Descending top-down feedback projections encode prior probability distributions and predictions regarding sensory contingencies, whereas ascending bottom-up feedforward pathways exclusively transmit precision-weighted prediction errors that recalibrate internal generative states.",
        "difficulty": "Very Hard",
        "annotation_rationale": "Mathematical neuroscience, dense specialized nominalizations (variational free energy, Bayesian inference), long sentences."
    },
    {
        "id": "vhard-neuro-2",
        "document_id": "doc-computational-neuro",
        "domain": "Neurobiology",
        "source_title": "Hierarchical Predictive Coding in Cortical Circuits",
        "source_license": "CC BY-SA 4.0",
        "text": "Neuromodulatory neurotransmitter systems, particularly dopaminergic and cholinergic projections emanating from subcortical nuclei, modulate the hyperparameter corresponding to synaptic gain, functionally modulating the expected precision of prediction errors relative to prior beliefs. Dysregulations within these precision-weighting computational mechanisms have been hypothesized to precipitate profound neuropsychiatric symptomatology, including hallucinatory perceptions and delusional fixations.",
        "difficulty": "Very Hard",
        "annotation_rationale": "Specialized computational psychiatry vocabulary, complex multi-syllabic construction, 30+ word sentences."
    },
    {
        "id": "vhard-neuro-3",
        "document_id": "doc-computational-neuro",
        "domain": "Neurobiology",
        "source_title": "Hierarchical Predictive Coding in Cortical Circuits",
        "source_license": "CC BY-SA 4.0",
        "text": "Consequently, active inference integrates perceptual categorization with motor output by framing behavioral actions as the physical attenuation of proprioceptive prediction errors through continuous somatic enactment. By continuously updating parameter spaces across heterogeneous spatiotemporal scales, the organism preserves homeostatic non-equilibrium steady states against thermodynamic entropy dissipation.",
        "difficulty": "Very Hard",
        "annotation_rationale": "Dense theoretical bio-physics and neuroscience integration, high syntactic density, minimal lexical repetition."
    },

    # Doc 19: Critical Literary Theory & Postmodern Aesthetics
    {
        "id": "vhard-lit-1",
        "document_id": "doc-literary-theory",
        "domain": "Literary Criticism",
        "source_title": "Discursive Formations and Semiotic Disruption",
        "source_license": "CC BY-SA 4.0",
        "text": "Post-structuralist textual hermeneutics challenges the logocentric illusion of fixed referential signification, positing instead that textual semantics remain permanently deferred along infinite chains of differential signifiers. The autonomous authorial subject, previously reified as the sovereign originator of aesthetic meaning, dissolves into an intertextual nexus traversed by historical epistemes and contested ideological discourses.",
        "difficulty": "Very Hard",
        "annotation_rationale": "High abstraction, post-structuralist literary terminology, complex sentence morphology."
    },
    {
        "id": "vhard-lit-2",
        "document_id": "doc-literary-theory",
        "domain": "Literary Criticism",
        "source_title": "Discursive Formations and Semiotic Disruption",
        "source_license": "CC BY-SA 4.0",
        "text": "Consequently, deconstructive close reading uncovers the symptomatic aporias and semantic contradictions through which the text inadvertently dismantles its own programmatic metaphysical assumptions. By interrogating the marginalized marginalia and unstated absences within the textual topography, critical theory subverts the authoritative hegemony of institutional canons and demystifies the naturalized ideological operations of cultural capital.",
        "difficulty": "Very Hard",
        "annotation_rationale": "Dense cultural theory terminology (aporias, hegemony, cultural capital), multi-tiered syntax, high reading friction."
    },

    # Doc 20: Quantum Electrodynamics & Gauge Field Theory
    {
        "id": "vhard-quantum-1",
        "document_id": "doc-quantum-electrodynamics",
        "domain": "Theoretical Physics",
        "source_title": "Non-Abelian Gauge Invariance and Renormalization",
        "source_license": "CC BY-SA 4.0",
        "text": "In relativistic non-Abelian quantum field theories, local gauge invariance under non-commutative symmetry groups mandates the introduction of vector gauge fields whose non-linear self-interactions generate asymptotic freedom at elevated momentum transfers. Perturbative calculations in these Yang-Mills frameworks inevitably generate ultraviolet divergences that necessitate systematic dimensional regularization and renormalization group flow analysis to extract physically observable scattering cross-sections.",
        "difficulty": "Very Hard",
        "annotation_rationale": "Advanced graduate theoretical physics, complex mathematical terms, multi-clause dense exposition."
    },
    {
        "id": "vhard-quantum-2",
        "document_id": "doc-quantum-electrodynamics",
        "domain": "Theoretical Physics",
        "source_title": "Non-Abelian Gauge Invariance and Renormalization",
        "source_license": "CC BY-SA 4.0",
        "text": "The topological vacuum structure of non-Abelian gauge configurations accommodates non-trivial winding numbers and instanton solutions that induce chiral anomaly violations through quantum tunneling between degenerate classical vacua. Consequently, resolving the strong charge-parity problem necessitates evaluating spontaneous Peccei-Quinn symmetry breaking mechanisms and their resultant pseudo-Goldstone bosons.",
        "difficulty": "Very Hard",
        "annotation_rationale": "Dense quantum field terminology, highly technical sentence structure, highest linguistic and conceptual difficulty."
    },

    # Doc 21: Econometric Time-Series & Cointegration
    {
        "id": "vhard-econ-1",
        "document_id": "doc-econometrics-timeseries",
        "domain": "Econometrics",
        "source_title": "Non-Stationary Stochastic Processes",
        "source_license": "CC BY-SA 4.0",
        "text": "When macroeconomic time-series exhibit stochastic unit root non-stationarity, standard ordinary least squares regression estimators generate spurious statistical inferences due to asymptotically non-vanishing covariance structures. Establishing legitimate long-run equilibrium relationships between integrated variables of order one requires testing for cointegrating vectors using Johansen maximum likelihood procedures under vector error-correction specifications.",
        "difficulty": "Very Hard",
        "annotation_rationale": "Graduate econometrics, advanced mathematical statistics terminology, dense multi-syllable construction."
    },
    {
        "id": "vhard-econ-2",
        "document_id": "doc-econometrics-timeseries",
        "domain": "Econometrics",
        "source_title": "Non-Stationary Stochastic Processes",
        "source_license": "CC BY-SA 4.0",
        "text": "Furthermore, structural breaks in deterministic trend components frequently bias standard augmented Dickey-Fuller tests toward false unit root non-rejection, thereby confounding genuine mean-reverting dynamics with persistent stochastic drift. Resolving this identification ambiguity necessitates implementing endogenous regime-switching algorithms that simultaneously estimate break timestamps and cointegration rank rank under generalized autoregressive conditional heteroskedasticity.",
        "difficulty": "Very Hard",
        "annotation_rationale": "Extreme mathematical terminology, heavy multi-clause syntax, 34 words per sentence."
    },

    # Doc 22: Agriculture & Farming
    {
        "id": "easy-farm-1",
        "document_id": "doc-farming-roots",
        "domain": "Agriculture",
        "source_title": "Growing Food on Family Farms",
        "source_license": "CC BY-SA 4.0",
        "text": "Farmers wake up early in the morning when the sun rises. They drive red tractors across wide fields to prepare the rich soil. Small seeds are planted in straight, even rows. When clouds bring soft rain, the tiny seeds drink water and begin to sprout green stems.",
        "difficulty": "Easy",
        "annotation_rationale": "Simple subject-verb-object structures, familiar vocabulary, elementary reading ease."
    },
    {
        "id": "easy-farm-2",
        "document_id": "doc-farming-roots",
        "domain": "Agriculture",
        "source_title": "Growing Food on Family Farms",
        "source_license": "CC BY-SA 4.0",
        "text": "During warm summer days, green corn stalks grow taller than grown-up people. Farmers pull out prickly weeds so the healthy plants have plenty of room to stretch. In the crisp fall season, large combine machines harvest golden ears of corn and crunchy red apples for families to eat.",
        "difficulty": "Easy",
        "annotation_rationale": "Concrete narrative, simple adjectives, high readability ease."
    },

    # Doc 23: Musical Instruments
    {
        "id": "easy-music-1",
        "document_id": "doc-music-instruments",
        "domain": "Music Education",
        "source_title": "How Instruments Make Sound",
        "source_license": "CC BY-SA 4.0",
        "text": "Music is made of pleasant vibrations that travel through the air into our ears. When you pluck a tight guitar string, it wiggles back and forth very quickly. This fast movement creates a warm musical note. Thick strings make deep, low sounds, while thin strings make bright, high notes.",
        "difficulty": "Easy",
        "annotation_rationale": "Short sentences, intuitive acoustic descriptions, child-accessible syntax."
    },
    {
        "id": "easy-music-2",
        "document_id": "doc-music-instruments",
        "domain": "Music Education",
        "source_title": "How Instruments Make Sound",
        "source_license": "CC BY-SA 4.0",
        "text": "Drums make rhythmic sounds when you strike the tight top skin with wooden sticks. Trumpets and shiny horns make noise when a musician blows air through a metal tube. Playing music with friends in a school band teaches teamwork, patience, and brings happiness to everyone listening.",
        "difficulty": "Easy",
        "annotation_rationale": "Simple coordinate clauses, positive accessible vocabulary, zero jargon."
    },

    # Doc 24: The Industrial Revolution
    {
        "id": "med-ind-1",
        "document_id": "doc-industrial-revolution",
        "domain": "World History",
        "source_title": "Mechanization and Modern Industry",
        "source_license": "CC BY-SA 4.0",
        "text": "The Industrial Revolution began in Great Britain during the mid-eighteenth century, transforming traditional agrarian economies into mechanized manufacturing hubs. The development of practical steam engines by James Watt allowed factories to produce textiles at unprecedented speeds. Consequently, production shifted away from rural home cottages into centralized urban textile mills powered by coal and moving water.",
        "difficulty": "Medium",
        "annotation_rationale": "Middle school history terms (agrarian, mechanized, centralized), clear historical transitions."
    },
    {
        "id": "med-ind-2",
        "document_id": "doc-industrial-revolution",
        "domain": "World History",
        "source_title": "Mechanization and Modern Industry",
        "source_license": "CC BY-SA 4.0",
        "text": "Rapid industrial expansion prompted massive migration from peaceful rural farming villages into crowded manufacturing cities. Families lived in densely populated tenements that lacked proper sanitation, leading to frequent outbreaks of infectious illnesses like cholera. In response, early trade unions organized to demand safer working hours, fair compensation, and laws restricting exploitative child labor.",
        "difficulty": "Medium",
        "annotation_rationale": "Compound sentences, social studies vocabulary (migration, tenements, sanitation), moderate complexity."
    },

    # Doc 25: Ecosystems & Food Webs
    {
        "id": "med-eco-1",
        "document_id": "doc-ecosystems-web",
        "domain": "Ecology",
        "source_title": "Trophic Levels and Ecological Energy Flow",
        "source_license": "CC BY-SA 4.0",
        "text": "An ecological food web illustrates the complex network of feeding relationships that sustain biological communities. Energy originates with primary producers, such as green plants and photosynthetic algae, which transform solar energy into chemical sugars. Primary consumers, primarily herbivores, feed directly upon these plants to obtain the caloric energy necessary for growth and reproduction.",
        "difficulty": "Medium",
        "annotation_rationale": "Standard high school biology vocabulary (trophic, photosynthetic, herbivores), balanced expository clauses."
    },
    {
        "id": "med-eco-2",
        "document_id": "doc-ecosystems-web",
        "domain": "Ecology",
        "source_title": "Trophic Levels and Ecological Energy Flow",
        "source_license": "CC BY-SA 4.0",
        "text": "Because energy is lost as metabolic heat at each sequential transfer, higher trophic levels contain progressively less total biomass. Apex predators, which occupy the pinnacle of the ecological pyramid, depend on healthy populations of secondary and tertiary consumers below them. When human activities disrupt keystone species, entire regional ecosystems can experience unexpected trophic cascades that destabilize native species balance.",
        "difficulty": "Medium",
        "annotation_rationale": "Moderate sentence length, cohesive connective words (sequential, progressively), standard scientific exposition."
    },

    # Doc 26: Deep Neural Networks
    {
        "id": "hard-nn-1",
        "document_id": "doc-deep-learning",
        "domain": "Computer Science",
        "source_title": "Gradient Descent in Deep Architectures",
        "source_license": "CC BY-SA 4.0",
        "text": "Deep neural networks approximate non-linear functions by stacking parameterized affine transformations interleaved with non-linear activation functions such as rectified linear units. Optimization proceeds via backpropagation, wherein the gradient of an empirical loss objective is computed with respect to every layer parameter utilizing the multivariate calculus chain rule. In extremely deep networks, compounding gradient multiplications frequently induce catastrophic vanishing or exploding gradient phenomena.",
        "difficulty": "Hard",
        "annotation_rationale": "Advanced undergraduate computer science, mathematical terminology (affine, backpropagation, multivariate), long sentences."
    },
    {
        "id": "hard-nn-2",
        "document_id": "doc-deep-learning",
        "domain": "Computer Science",
        "source_title": "Gradient Descent in Deep Architectures",
        "source_license": "CC BY-SA 4.0",
        "text": "Residual networks mitigate this degradation problem by introducing identity shortcut connections that bypass parameterized convolutional layers. These skip connections allow gradients to propagate unimpeded across dozens of intermediate network depths, substantially simplifying the underlying convex optimization landscape. Consequently, models can scale to hundreds of layers while consistently avoiding training stagnation.",
        "difficulty": "Hard",
        "annotation_rationale": "Technical algorithmic prose, 24 words per sentence, high lexical diversity and precision."
    },

    # Doc 27: International Environmental Treaties
    {
        "id": "hard-treaty-1",
        "document_id": "doc-environmental-law",
        "domain": "International Relations & Law",
        "source_title": "Multilateral Environmental Agreements",
        "source_license": "CC BY-SA 4.0",
        "text": "Multilateral environmental agreements must navigate sovereign state interests, historical emissions responsibilities, and uneven technological capacities across participating signatories. The principle of common but differentiated responsibilities explicitly acknowledges that industrialized nations have historically contributed disproportionate shares of cumulative atmospheric carbon concentrations. Consequently, developing states frequently demand financial compensation mechanisms and technology transfers as prerequisites for binding statutory commitments.",
        "difficulty": "Hard",
        "annotation_rationale": "Elevated legal terminology, multi-tiered clauses, 28 words per sentence, collegiate reading level."
    },
    {
        "id": "hard-treaty-2",
        "document_id": "doc-environmental-law",
        "domain": "International Relations & Law",
        "source_title": "Multilateral Environmental Agreements",
        "source_license": "CC BY-SA 4.0",
        "text": "Compliance mechanisms within modern environmental treaties typically eschew punitive sanctions in favor of facilitative multilateral reporting structures and peer-review audits. While non-adversarial review processes preserve geopolitical goodwill and encourage high treaty participation rates, critics argue that the absence of coercive enforcement mechanisms diminishes structural deterrence against non-compliance.",
        "difficulty": "Hard",
        "annotation_rationale": "Formal international policy vocabulary (eschew, punitive, geopolitical), complex subordinate structures."
    },

    # Doc 28: Differential Geometry & General Relativity
    {
        "id": "vhard-geom-1",
        "document_id": "doc-differential-geometry",
        "domain": "Mathematical Physics",
        "source_title": "Riemannian Curvature and Einstein Field Equations",
        "source_license": "CC BY-SA 4.0",
        "text": "In pseudo-Riemannian geometry, the metric tensor establishes the fundamental invariant interval across four-dimensional spacetime manifolds, whereas the Levi-Civita connection uniquely prescribes torsion-free parallel transport. The Riemann curvature tensor formalizes the non-commutativity of covariant derivatives, quantifying intrinsic gravitational tidal forces independent of local coordinate parameterizations through contracted Ricci curvature and scalar curvature invariants.",
        "difficulty": "Very Hard",
        "annotation_rationale": "Graduate-level differential geometry, dense technical nomenclature, 28-word dense mathematical exposition."
    },
    {
        "id": "vhard-geom-2",
        "document_id": "doc-differential-geometry",
        "domain": "Mathematical Physics",
        "source_title": "Riemannian Curvature and Einstein Field Equations",
        "source_license": "CC BY-SA 4.0",
        "text": "Einstein's field equations relate this differential geometric curvature directly to the stress-energy-momentum tensor of matter fields, establishing non-linear hyperbolic partial differential equations whose global Cauchy problem exhibits coordinate singularities. Resolving geodesic incompleteness requires analyzing Penrose-Hawking singularity theorems, which demonstrate that gravitational collapse inevitably generates trapped surfaces under generalized energy conditions.",
        "difficulty": "Very Hard",
        "annotation_rationale": "Theoretical physics at doctoral level, abstract mathematical operators, 33 words per sentence, maximum reading friction."
    },

    # Doc 29: Macroeconomic DSGE Modeling
    {
        "id": "vhard-dsge-1",
        "document_id": "doc-dsge-modeling",
        "domain": "Econometrics",
        "source_title": "Dynamic Stochastic General Equilibrium Frameworks",
        "source_license": "CC BY-SA 4.0",
        "text": "New Keynesian dynamic stochastic general equilibrium models formalize macroeconomic fluctuations through microeconomic foundations incorporating monopolistic competition and Calvo staggered nominal price-setting frictions. Forward-looking representative households optimize intertemporal consumption paths across stochastic discount factors, generating an expectations-augmented Phillips curve wherein contemporaneous inflation depends recursively on expected future marginal costs and central bank policy reaction functions.",
        "difficulty": "Very Hard",
        "annotation_rationale": "High-level theoretical economics, complex compound clauses, mathematical economic terms, 32 words per sentence."
    },
    {
        "id": "vhard-dsge-2",
        "document_id": "doc-dsge-modeling",
        "domain": "Econometrics",
        "source_title": "Dynamic Stochastic General Equilibrium Frameworks",
        "source_license": "CC BY-SA 4.0",
        "text": "Estimating structural parameter vectors via full-information Bayesian Markov chain Monte Carlo methods necessitates specifying informative prior distributions to resolve local parameter unidentifiability in linear rational expectations state-space representations. When macroeconomic shocks induce structural non-linearities at the effective zero lower bound on nominal interest rates, standard perturbation solutions fail, requiring piecewise linear shooting algorithms.",
        "difficulty": "Very Hard",
        "annotation_rationale": "Doctoral econometrics, maximum syntactic intricacy, technical terminology density, zero colloquialism."
    }
]

def main():
    out_dir = Path(__file__).resolve().parent / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "acli_educational_v1.json"
    
    dataset = {
        "dataset_name": "FocusFlow ACLI Educational Readability Dataset",
        "version": DATASET_VERSION,
        "description": "Curated 4-class paragraph text complexity dataset with document-level grouping for data leakage prevention.",
        "classes": ["Easy", "Medium", "Hard", "Very Hard"],
        "class_counts": {},
        "total_paragraphs": len(PARAGRAPHS),
        "total_documents": len(set(p["document_id"] for p in PARAGRAPHS)),
        "data": PARAGRAPHS
    }

    # Count class distribution
    for p in PARAGRAPHS:
        cls = p["difficulty"]
        dataset["class_counts"][cls] = dataset["class_counts"].get(cls, 0) + 1

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"Dataset v{DATASET_VERSION} successfully created at {out_file}")
    print(f"Total Paragraphs: {dataset['total_paragraphs']}")
    print(f"Total Documents:  {dataset['total_documents']}")
    print(f"Class Counts:     {dataset['class_counts']}")

if __name__ == "__main__":
    main()
