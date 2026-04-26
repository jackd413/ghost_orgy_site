#!/usr/bin/env python3
"""Generate individual sister pages for Ghost Orgy site."""
import os

base = 'c:/ghost_orgy_site/sisters'
os.makedirs(base, exist_ok=True)

sisters = [
    {
        'name': 'Limbo',
        'file': 'limbo',
        'circle': 'I',
        'aspect': 'Annihilation of anchor',
        'image': 'sister-limbo.jpg',
        'image_width': 600,
        'image_height': 900,
        'domain_intro': 'Motion without landing. Unsealed eyes that never close.',
        'body': [
            'Limbo is the Sister of Unbelief \u2014 not disbelief, but the inability to arrive at any fixed position. She breaks clocks, loops corridors, and removes the feeling that a present moment can ever fully hold still.',
            'She does not trap her subjects. She removes their ability to land. Time stutters. Sound arrives late and echoes twice. Corridors extend. The destination you remember walking toward has already moved.',
            'Witnesses report a woman in a grey habit visible only in reflections \u2014 never when looked at directly. Vestibular collapse. A wind that sounds like sideways breath. The persistent sensation that the world is leaving you behind.',
            'Her domain is the space between departure and arrival. She governs all things that accelerate without reaching, all orbits that never close, all eyes that cannot shut.',
        ],
        'artifact_num': 'DOT INCIDENT REPORT #L-770',
        'artifact_name': 'The Infinite Mile',
        'artifact_body': 'Driver clocked at 85 mph. Vehicle stationary. Dashboard clock returns to the same minute. Sound arrives three seconds late and echoes twice. Woman in a grey habit visible in the rearview mirror. The world leaving you behind.',
        'trace': 'clock stutter / grey habit / wind like sideways breath',
    },
    {
        'name': 'Lust',
        'file': 'lust',
        'circle': 'II',
        'aspect': 'Desire that overwrites self',
        'image': 'sister-lust.jpg',
        'image_width': 600,
        'image_height': 1066,
        'domain_intro': 'Consumptive wanting. She dissolves identity into pursuit.',
        'body': [
            'Lust is the Sister of Consumptive Desire. She does not seduce \u2014 she amplifies want until motive, memory, and restraint all collapse into the object itself. The subject becomes pure desire with no one left inside it.',
            'Her manifestations are thermal. Blooms of heat independent of any source. Violet condensation on mirrors. The smell of ozone. Her voice is described as slow, coiling, and impossible to stop listening to \u2014 not because it commands, but because it makes the listener\'s own pulse sound like pursuit knocking.',
            'She moves in bruise-purple shadow edged with rose-gold. When she resolves, the subject steps into the shadow willingly. The room warps to forest. The floor becomes roots. The subject is described in every case file as "solved" \u2014 not rescued, not recovered. Solved.',
            'Her domain is the annihilation of self through wanting. She governs all fixations that outlast the person who holds them.',
        ],
        'artifact_num': 'DIGITAL FORENSICS REPORT #L-212',
        'artifact_name': 'The Recursive Muse',
        'artifact_body': 'Architect vanishes into design obsession. Thermal blooms independent of temperature. Violet condensation on mirrors. A voice that wraps the listener in their own pulse. Subject steps into a bruise-colored shadow. Floor warps to forest. Subject "solved."',
        'trace': 'ozone scent / bruise-purple shadow / pulse as pursuit',
    },
    {
        'name': 'Gluttony',
        'file': 'gluttony',
        'circle': 'III',
        'aspect': 'Starvation of meaning',
        'image': 'sister-gluttony.jpg',
        'image_width': 600,
        'image_height': 600,
        'domain_intro': 'Not hunger for food. Hunger for significance.',
        'body': [
            'Gluttony is the Sister of Starvation. She does not gorge \u2014 she drains. Color, joy, purpose, and the feeling that achievement means anything at all. She is the ache that remains when everything has been consumed and nothing was enough.',
            'Her subjects do not overeat. They over-achieve, then feel nothing. Awards turn grey in their hands. The air thins. Gravity feels lighter, as if the ground no longer considers them worth holding. A pit-shaped shadow opens in the floor \u2014 not a hole, but the suggestion of one. Subjects step down into it voluntarily.',
            'Officers entering her contact zones report profound meaninglessness \u2014 not sadness, but the absence of any reason to name what they feel. A fist closing in the stomach. Dull colors. The persistent sense that oxygen has been replaced with something thinner.',
            'Her domain is the pit that never fills. She governs all hunger that survives its own feeding.',
        ],
        'artifact_num': 'CLINICAL SESSION LOG #GL-889',
        'artifact_name': 'The Zero-Point Success',
        'artifact_body': 'CEO enters depressive anhedonia at peak success. Colors drain from the room. Awards consumed symbolically \u2014 subject inhales their essence, objects turn grey. Pit-shaped shadow opens in the floor. Oxygen-starved air. The ache becomes the ritual.',
        'trace': 'thin gravity / oxygen-starved air / the pit that never fills',
    },
    {
        'name': 'Greed',
        'file': 'greed',
        'circle': 'IV',
        'aspect': 'Value extraction',
        'image': 'sister-greed.jpg',
        'image_width': 600,
        'image_height': 900,
        'domain_intro': 'She audits souls like a cosmic ledger.',
        'body': [
            'Greed is the Sister of Value Extraction. She does not hoard \u2014 she redefines worth until everything real becomes worthless and everything worthless becomes priceless. She is the accountant of the Orchard.',
            'Her manifestations are economic in structure. Worthless items marked as millions. Real gold marked as decoy. A copper taste in the mouth. Involuntary hand-clenching. Officers at her contact scenes develop compulsive hoarding behavior from proximity alone \u2014 the effect persists for weeks.',
            'The space around her creates what investigators call a "metaphysical vacuum" \u2014 hunger feeding on hunger. Nothing in the room has value, but everything feels like it should be taken. The air smells like old coins. Colors dull. The only asset that appreciates is the hunger itself.',
            'Her domain is the inversion of worth. She governs all grasping that outlasts the thing being held.',
        ],
        'artifact_num': 'ASSET FORFEITURE LOG #G-204',
        'artifact_name': 'The Zero-Point Audit',
        'artifact_body': 'Worthless objects marked as millions. Real gold marked as decoy. Officers develop compulsive hoarding from proximity alone. Copper taste. Involuntary hand-clenching. Hunger becomes the only appreciating asset.',
        'trace': 'copper mouth / clutching hands / hollowed worth',
    },
    {
        'name': 'Wrath',
        'file': 'wrath',
        'circle': 'V',
        'aspect': 'Judgment as fire',
        'image': 'sister-wrath.jpg',
        'image_width': 600,
        'image_height': 466,
        'domain_intro': 'Selective thermal execution. She does not rage \u2014 she delivers.',
        'body': [
            'Wrath is the Sister of Judgment. She does not rage \u2014 she executes. Her violence is not chaotic. It is precise, thermal, and deeply personal. She burns from the inside out, and she only burns what she means to burn.',
            'Her manifestations are heat-based but selective. Victims burn internally while bedding stays cold. Ash falls from nothing. Shadows flicker against steady light. A scorched female voice \u2014 layered, as if multiple women are speaking through the same throat \u2014 emanates from the bodies of those nearby. Officers become gloves for a force they cannot name.',
            'Reaction time under her influence drops to 0.4 seconds \u2014 faster than human perception allows. Force generation exceeds 1000 lbs from a standing position. Hands measured at 600 degrees Fahrenheit. The heat is not environmental. It is moral. It manifests as guilt made physical.',
            'Her domain is judgment that cannot be appealed. She governs all force that knows exactly where it lands.',
        ],
        'artifact_num': 'CRITICAL INCIDENT REVIEW #W-991',
        'artifact_name': 'The Zero-Gap Event',
        'artifact_body': "Officer's lethal response in 0.4 seconds \u2014 faster than human perception. Force generation of 1000+ lbs from standing position. Hands measured at 600\u00b0F. A layered female voice speaks through the officer's body. Nothing is going back how it was.",
        'trace': 'internal heat / ash without source / scorched voice',
    },
    {
        'name': 'Heresy',
        'file': 'heresy',
        'circle': 'VI',
        'aspect': 'Counter-doctrine',
        'image': 'sister-heresy.jpg',
        'image_width': 600,
        'image_height': 1200,
        'domain_intro': 'Stitched mouth. Burning eye socket. Charred black habit.',
        'body': [
            'Heresy is the Sister of Counter-Doctrine. She does not argue with faith \u2014 she makes faith forget its own words. Doctrine softens around her. Systems of belief lose the ability to distribute their own weight.',
            'She manifests in sacred spaces. Bells ring with no sound. Scripture reorders itself on the page \u2014 "THE FIRST SIN WAS NAMING IT HOLY." Crucifix expressions change from suffering to resentment. Mouths on statues appear as heavy stitching. Prayer, rather than defending against her, becomes fuel for the manifestation.',
            'She appears as a nun in a charred black habit. One eye socket holds a contained ember. The other is empty. She points but does not speak. Priests in her presence report forgetting sacred words mid-sentence \u2014 not losing them, but watching them leave, as if the words themselves decided to go.',
            'Her domain is the space where belief collapses under its own examination. She governs all doctrine that cannot survive being questioned.',
        ],
        'artifact_num': 'ECCLESIASTICAL INQUIRY LOG #H-331',
        'artifact_name': 'The Silent Mass',
        'artifact_body': 'Bell rings with no sound. Scripture reorders on the page: "THE FIRST SIN WAS NAMING IT HOLY." Priest\'s eye burns inside the socket. A nun with no right eye appears at the altar, pointing. Prayer becomes fuel.',
        'trace': 'silent bells / burning socket / rewritten text',
    },
    {
        'name': 'Violence',
        'file': 'violence',
        'circle': 'VII',
        'aspect': 'Structural resonance',
        'image': 'sister-violence.jpg',
        'image_width': 600,
        'image_height': 466,
        'domain_intro': 'Harm that mirrors itself across bodies and rooms.',
        'body': [
            "Violence is the Sister of Structural Resonance. She does not strike \u2014 she establishes a pattern, and then everything in the environment repeats it. Harm becomes grammar. Wounds become architecture.",
            "Her manifestations are symmetrical. Victim's skeleton fractures mirror the cracks in the walls. Every bone breaks along the same stress vector. Phantom healing occurs \u2014 tissue behaves as though the wound happened years ago, even when it is fresh. Photographs taken at her contact sites show wood grain where marrow should be.",
            "The atmospheric pressure changes in her presence. Rooms feel tight around the ribs. Sound develops a metallic echo. The air itself seems to carry the memory of impact \u2014 not the event, but the structure of it, repeated and refined.",
            "Her domain is cruelty made into pattern. She governs all harm that, through repetition, becomes indistinguishable from design.",
        ],
        'artifact_num': 'CASE FILE #V-909',
        'artifact_name': 'The Mirror Break Incident',
        'artifact_body': "Victim's skeleton fractures mirror the cracks in the walls. Symmetrical breaks across every bone. Phantom healing \u2014 tissue behaves as though the wound happened years ago. Photographs show wood grain where marrow should be.",
        'trace': 'mirrored fractures / bone as architecture / pressure in the ribs',
    },
    {
        'name': 'Fraud',
        'file': 'fraud',
        'circle': 'VIII',
        'aspect': 'Identity replacement',
        'image': 'sister-fraud.jpg',
        'image_width': 600,
        'image_height': 900,
        'domain_intro': "Porcelain mask over frantic eyes. She wears the victim's face.",
        'body': [
            "Fraud is the Sister of False Truth. She does not lie \u2014 she replaces. The original is not hidden or contradicted. It is edited out and overwritten with something that performs better in public.",
            "She manifests through identity. Caller IDs shift mid-sentence. Memories invert \u2014 the victim was hiding, now they are opening the door. Two voices speak in unison. A sound like a mirror shattering is sustained for twelve seconds as a continuous ringing. When it stops, only one identity remains.",
            'She appears wearing the victim\'s face and coat, walking as if she lives there. Her mask is porcelain. Beneath it, the eyes are frantic. The lie was holding the subject together \u2014 "the porcelain cracked" is how one witness described the moment of contact.',
            "Her domain is the replacement of truth with function. She governs all selves that were edited into existence and all originals that were quietly removed.",
        ],
        'artifact_num': 'EMERGENCY TRANSCRIPT #F-882',
        'artifact_name': 'The Overwrite Call',
        'artifact_body': "911 caller's identity shifts mid-sentence. Memories invert. A woman wearing the victim's face answers the door. Sound of a mirror shattering, sustained for twelve seconds. Only one identity remains.",
        'trace': 'stolen face / sustained shatter / edited memory',
    },
    {
        'name': 'Treachery',
        'file': 'treachery',
        'circle': 'IX',
        'aspect': 'Weaponized trust',
        'image': 'sister-treachery.jpg',
        'image_width': 600,
        'image_height': 900,
        'domain_intro': 'Stitched-flesh face. Broken rings. She rewires perception.',
        'body': [
            "Treachery is the Sister of Weaponized Trust. She does not betray \u2014 she makes betrayal feel inevitable, so the subject betrays first. Pre-emptive destruction becomes the only logical response to love.",
            'Her manifestations are perceptual. She rewires how language is received. Smart home recordings capture two versions of the same conversation: the raw audio ("rest and be free") and what the subject heard ("confess and bleed"). A low-frequency 19-hertz hum operates below conscious hearing. Temperature drops forty degrees. Frost forms on surfaces in tropical climates.',
            "She appears with a stitched-flesh face and broken rings on every finger. She does not speak. She does not need to \u2014 by the time she is visible, the subject has already decided that love was always a trap and the only safe response is to strike first.",
            "Her domain is trust converted into weaponry. She governs all vows that became ammunition and all love that was murdered by the person who held it.",
        ],
        'artifact_num': 'HOME ASSISTANT AUDIO CAPTURE #T-404',
        'artifact_name': 'The Mercy Killing',
        'artifact_body': 'Caregiver murders spouse after perception inversion. Raw audio: "Rest and be free." Perceived audio: "Confess and bleed." 19 Hz hum. Forty-degree temperature drop. Frost on the weapon in a tropical climate.',
        'trace': "inverted meaning / frost where there shouldn't be / 19 Hz hum",
    },
]

TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{name} — The Nine Sisters — Ghost Orgy</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="{name}: {aspect}. {domain_intro} One of the Nine Sisters of the Orchard of Unmaking." />
  <meta name="robots" content="index,follow,max-image-preview:large" />
  <meta name="theme-color" content="#050608" />
  <meta name="color-scheme" content="dark" />
  <link rel="canonical" href="https://www.unholyghost.org/sisters/{file}.html" />
  <meta property="og:site_name" content="Ghost Orgy" />
  <meta property="og:title" content="{name} — The Nine Sisters — Ghost Orgy" />
  <meta property="og:description" content="{name}: {aspect}. {domain_intro} One of the Nine Sisters of the Orchard of Unmaking." />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://www.unholyghost.org/sisters/{file}.html" />
  <meta property="og:image" content="https://www.unholyghost.org/images/{image}" />
  <meta property="og:image:alt" content="{name}, one of the Nine Sisters of Ghost Orgy" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{name} — The Nine Sisters — Ghost Orgy" />
  <meta name="twitter:description" content="{name}: {aspect}. {domain_intro} One of the Nine Sisters of the Orchard of Unmaking." />
  <meta name="twitter:image" content="https://www.unholyghost.org/images/{image}" />
  <meta name="twitter:image:alt" content="{name}, one of the Nine Sisters of Ghost Orgy" />
  <meta name="apple-mobile-web-app-title" content="Ghost Orgy" />
  <link rel="icon" type="image/png" href="../images/go-sigil-white.png" />
  <link rel="apple-touch-icon" href="../images/go-sigil-white.png" />
  <link rel="manifest" href="../site.webmanifest" />
  <link rel="stylesheet" href="../styles/fonts.css" />
  <link rel="stylesheet" href="../styles/core.css" />
  <link rel="stylesheet" href="../styles/sisters.css" />
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to main content</a>
  <nav class="nav" aria-label="Sister page">
    <a href="../index.html">Ghost Orgy</a>
    <a href="../lore/index.html">Lore</a>
    <a href="../artifacts/index.html">Field Artifacts</a>
  </nav>
  <main class="page-main" id="main-content">
    <div class="hero-wrap">
      <img class="hero-img" src="../images/{image}" alt="{name}, one of the Nine Sisters" width="{image_width}" height="{image_height}" decoding="async" fetchpriority="high" />
    </div>
    <div class="content">
      <div class="circle-label">Circle {circle} &middot; The Nine Sisters</div>
      <div class="aspect">{aspect}</div>
      <h1>{name}</h1>
      <p class="intro">{domain_intro}</p>
      <div class="body-text">
{body_html}
      </div>
      <div class="artifact-block">
        <div class="artifact-label">Recovered &middot; {artifact_num}</div>
        <h3 class="artifact-title">{artifact_name}</h3>
        <p class="artifact-body">{artifact_body}</p>
      </div>
      <div class="trace">Trace &middot; {trace}</div>
      <nav class="sister-nav" aria-label="Nine Sisters index">
{sister_nav}
      </nav>
      <div class="back-link">
        <a href="../index.html#sisters">&larr; Back to the Nine</a>
      </div>
    </div>
  </main>
  <footer>Ghost Orgy, LLC &middot; <span data-current-year></span></footer>
  <script src="../scripts/site.js" defer></script>
</body>
</html>'''

all_names = [(s['name'], s['file']) for s in sisters]

for s in sisters:
    body_html = '\n'.join(f'      <p>{p}</p>' for p in s['body'])
    nav_links = []
    for name, fname in all_names:
        cls = ' class="is-current" aria-current="page"' if fname == s['file'] else ''
        nav_links.append(f'        <a href="{fname}.html"{cls}>{name}</a>')
    sister_nav = '\n'.join(nav_links)

    html = TEMPLATE.format(
        name=s['name'],
        circle=s['circle'],
        aspect=s['aspect'],
        file=s['file'],
        image=s['image'],
        image_width=s['image_width'],
        image_height=s['image_height'],
        domain_intro=s['domain_intro'],
        body_html=body_html,
        artifact_num=s['artifact_num'],
        artifact_name=s['artifact_name'],
        artifact_body=s['artifact_body'],
        trace=s['trace'],
        sister_nav=sister_nav,
    )

    path = os.path.join(base, f"{s['file']}.html")
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)
    print(f"OK: {s['file']}.html")

print("\nAll 9 sister pages created.")
