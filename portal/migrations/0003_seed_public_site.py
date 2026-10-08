from django.db import migrations


SITE_TRANSLATIONS = {
    "s1k": {
        "fr": "Avocats & Conseils juridiques · Nouakchott",
        "ar": "محاماة واستشارات قانونية · انواكشوط",
        "en": "Attorneys & Legal Counsel · Nouakchott",
    },
    "s1t": {
        "fr": "Le droit, défendu avec rigueur et discrétion.",
        "ar": "ندافع عن حقوقكم بصرامة وتكتّم.",
        "en": "The law, defended with rigour and discretion.",
    },
    "s1p": {
        "fr": "Conseil et représentation devant les juridictions mauritaniennes, pour les entreprises comme pour les particuliers.",
        "ar": "استشارة وتمثيل أمام المحاكم الموريتانية، للشركات والأفراد على حد سواء.",
        "en": "Advice and representation before the Mauritanian courts, for businesses and individuals alike.",
    },
    "c_h": {
        "fr": "Un cabinet d'avocats et de conseils juridiques au cœur de Nouakchott.",
        "ar": "مكتب للمحاماة والاستشارات القانونية في قلب انواكشوط.",
        "en": "A law and legal advisory firm in the heart of Nouakchott.",
    },
    "c_p1": {
        "fr": "Fondé par le Dr. Bahou Dahoud, docteur en droit privé, le Cabinet Dahoud accompagne ses clients en conseil comme en contentieux, devant l'ensemble des tribunaux mauritaniens.",
        "ar": "أسسه الدكتور باهو دحود، الدكتور في القانون الخاص، ويرافق مكتب دحود موكليه في الاستشارة والتقاضي أمام مختلف المحاكم الموريتانية.",
        "en": "Founded by Dr. Bahou Dahoud, Doctor of Private Law, the Dahoud Law Firm supports clients in advisory and litigation work before Mauritanian courts.",
    },
    "c_p2": {
        "fr": "Le cabinet privilégie les solutions négociées lorsqu'elles servent vos intérêts et défend vos droits avec détermination lorsque le procès s'impose.",
        "ar": "يفضّل المكتب الحلول الودية عندما تخدم مصالحكم، ويدافع عن حقوقكم بحزم عندما تقتضي الحاجة اللجوء إلى القضاء.",
        "en": "The firm favours negotiated solutions where they serve your interests, and defends your rights resolutely when litigation is necessary.",
    },
    "f_name": {
        "fr": "Dr. Bahou DAHOUD",
        "ar": "الدكتور باهو دحود",
        "en": "Dr. Bahou DAHOUD",
    },
    "f_t1": {
        "fr": "Docteur en droit privé",
        "ar": "دكتور في القانون الخاص",
        "en": "Doctor of Private Law",
    },
    "f_t2": {
        "fr": "Avocat agréé près des tribunaux mauritaniens",
        "ar": "محام معتمد لدى المحاكم الموريتانية",
        "en": "Attorney admitted before Mauritanian courts",
    },
    "f_bio": {
        "fr": "Le Dr. Bahou Dahoud dirige le cabinet et suit personnellement les dossiers qui lui sont confiés, en conseil comme devant les juridictions.",
        "ar": "يدير الدكتور باهو دحود المكتب ويتابع شخصياً الملفات الموكلة إليه، استشارةً وتقاضياً.",
        "en": "Dr. Bahou Dahoud heads the firm and personally oversees the matters entrusted to him, in advisory work and in court.",
    },
    "e_h": {
        "fr": "Des compétences au service de vos droits",
        "ar": "خبرات في خدمة حقوقكم",
        "en": "Expertise in the service of your rights",
    },
    "e_p": {
        "fr": "Conseil, rédaction d'actes et représentation devant les juridictions mauritaniennes.",
        "ar": "استشارات وصياغة عقود وتمثيل أمام المحاكم الموريتانية.",
        "en": "Advice, drafting and representation before Mauritanian courts.",
    },
    "g_h": {
        "fr": "Le cabinet en images",
        "ar": "المكتب بالصور",
        "en": "The firm in pictures",
    },
    "g_p": {
        "fr": "Architecture, recherche juridique et lieux de savoir.",
        "ar": "العمارة والبحث القانوني وفضاءات المعرفة.",
        "en": "Architecture, legal research and places of learning.",
    },
    "q_h": {
        "fr": "Avant de prendre rendez-vous",
        "ar": "قبل حجز موعد",
        "en": "Before your appointment",
    },
    "k_h": {
        "fr": "Contacter le Cabinet Dahoud",
        "ar": "تواصلوا مع مكتب دحود",
        "en": "Contact Dahoud Law Firm",
    },
    "addr": {
        "fr": "Résidence Al-Najah – Sokouk N° 139, 1er étage, Bureau N° 4, Nouakchott, Mauritanie",
        "ar": "عمارة النجاح - صكوك رقم 139، الطابق الأول، مكتب رقم 4، انواكشوط - موريتانيا",
        "en": "Al-Najah Residence – Sokouk No. 139, 1st floor, Office No. 4, Nouakchott, Mauritania",
    },
    "hours": {
        "fr": "Sur rendez-vous",
        "ar": "بموعد مسبق",
        "en": "By appointment",
    },
    "ft_desc": {
        "fr": "Avocats & Conseils juridiques. Conseil et contentieux pour entreprises et particuliers, à Nouakchott.",
        "ar": "محاماة واستشارات قانونية للشركات والأفراد في انواكشوط.",
        "en": "Attorneys and legal counsel for businesses and individuals in Nouakchott.",
    },
}


def seed_public_site(apps, schema_editor):
    SiteSettings = apps.get_model("portal", "SiteSettings")
    PracticeArea = apps.get_model("portal", "PracticeArea")
    GalleryPhoto = apps.get_model("portal", "GalleryPhoto")
    TeamMember = apps.get_model("portal", "TeamMember")
    Publication = apps.get_model("portal", "Publication")

    SiteSettings.objects.update_or_create(
        pk=1,
        defaults={
            "translations": SITE_TRANSLATIONS,
            "telephone": "+222 47 03 03 04",
            "whatsapp": "+222 31 03 03 06, +222 22 03 03 01",
            "telephone_fixe": "+222 47 99 99 01, +222 45 25 71 29",
            "email": "dahoudavocat@gmail.com",
            "site_web": "www.avocat-dahoud.com",
            "adresse": "Résidence Al-Najah – Sokouk N° 139, 1er étage, Bureau N° 4, Nouakchott, Mauritanie",
            "heures": "Sur rendez-vous",
            "adresse_carte": "Résidence Al-Najah, Sokouk N° 139, Nouakchott, Mauritanie",
        },
    )

    practices = [
        (
            "Droit des affaires",
            "قانون الأعمال",
            "Business law",
            "Création et vie des sociétés, contrats commerciaux et recouvrement de créances.",
            "تأسيس الشركات ومتابعة شؤونها والعقود التجارية وتحصيل الديون.",
            "Company formation, commercial contracts and debt recovery.",
        ),
        (
            "Droit du travail",
            "قانون العمل",
            "Employment law",
            "Contrats de travail, relations employeur-salarié et contentieux devant le tribunal du travail.",
            "عقود العمل وعلاقات المشغّل بالأجير والنزاعات أمام محكمة الشغل.",
            "Employment contracts, workplace relations and labour disputes.",
        ),
        (
            "Droit pénal",
            "القانون الجنائي",
            "Criminal law",
            "Assistance en garde à vue, défense pénale et constitution de partie civile.",
            "المؤازرة أثناء التوقيف والدفاع الجنائي والتأسيس طرفاً مدنياً.",
            "Police-station assistance, criminal defence and civil-party representation.",
        ),
        (
            "Famille et personnes",
            "الأسرة والأحوال الشخصية",
            "Family and personal status",
            "Mariage, divorce, garde des enfants, pension alimentaire et successions.",
            "الزواج والطلاق وحضانة الأطفال والنفقة والتركات.",
            "Marriage, divorce, child custody, maintenance and inheritance.",
        ),
        (
            "Foncier et immobilier",
            "العقار والأراضي",
            "Property law",
            "Titres fonciers, baux et litiges de voisinage ou de construction.",
            "الملكية العقارية والإيجار والنزاعات المتعلقة بالعقار والبناء.",
            "Land titles, leases and property or construction disputes.",
        ),
        (
            "Droit administratif",
            "القانون الإداري",
            "Administrative law",
            "Marchés publics et recours contre les décisions de l'administration.",
            "الصفقات العمومية والطعون في قرارات الإدارة.",
            "Public procurement and challenges to administrative decisions.",
        ),
    ]
    for position, values in enumerate(practices, start=1):
        PracticeArea.objects.update_or_create(
            title_fr=values[0],
            defaults={
                "title_ar": values[1],
                "title_en": values[2],
                "description_fr": values[3],
                "description_ar": values[4],
                "description_en": values[5],
                "icon": position,
                "position": position,
                "is_active": True,
            },
        )

    photos = [
        (
            "/static/images/mosque-sheikh-zayed.jpg",
            "Architecture de la grande mosquée d'Abou Dabi",
            "عمارة جامع الشيخ زايد الكبير",
            "Architecture of the Sheikh Zayed Grand Mosque",
            True,
        ),
        (
            "/static/images/law-library.jpg",
            "Bibliothèque et ouvrages juridiques",
            "مكتبة ومراجع قانونية",
            "Law library and legal books",
            True,
        ),
        (
            "/static/images/mosque-aerial.jpg",
            "Architecture d'une mosquée au coucher du soleil",
            "عمارة مسجد عند الغروب",
            "Mosque architecture at sunset",
            True,
        ),
    ]
    for position, values in enumerate(photos, start=1):
        GalleryPhoto.objects.update_or_create(
            image_url=values[0],
            defaults={
                "caption_fr": values[1],
                "caption_ar": values[2],
                "caption_en": values[3],
                "position": position,
                "is_slide": values[4],
                "is_active": True,
            },
        )

    TeamMember.objects.update_or_create(
        name_fr="Dr. Bahou DAHOUD",
        defaults={
            "name_ar": "الدكتور باهو دحود",
            "name_en": "Dr. Bahou DAHOUD",
            "title_fr": "Docteur en droit privé · Avocat agréé",
            "title_ar": "دكتور في القانون الخاص · محام معتمد",
            "title_en": "Doctor of Private Law · Admitted attorney",
            "bio_fr": "Le Dr. Bahou Dahoud dirige le cabinet et suit personnellement les dossiers qui lui sont confiés, en conseil comme devant les juridictions.",
            "bio_ar": "يدير الدكتور باهو دحود المكتب ويتابع شخصياً الملفات الموكلة إليه، استشارةً وتقاضياً.",
            "bio_en": "Dr. Bahou Dahoud heads the firm and personally oversees the matters entrusted to him, in advisory work and in court.",
            "credentials_fr": ["Doctorat en droit privé", "Avocat agréé près des tribunaux mauritaniens"],
            "credentials_ar": ["دكتوراه في القانون الخاص", "محام معتمد لدى المحاكم الموريتانية"],
            "credentials_en": ["Doctorate in Private Law", "Admitted attorney before Mauritanian courts"],
            "position": 1,
            "is_active": True,
        },
    )

    publications = [
        (
            "Droit du travail",
            "Employment law",
            "قانون العمل",
            "Licenciement : ce qu'il faut vérifier avant d'agir",
            "Dismissal: what to check before taking action",
            "الفصل من العمل: ما يجب التحقق منه قبل اتخاذ إجراء",
            "Motif, procédure, délais pour contester : les points à rassembler avant un premier rendez-vous.",
            "Grounds, procedure and deadlines: what to prepare before your first appointment.",
            "الأسباب والإجراءات والآجال: ما ينبغي تحضيره قبل الموعد الأول.",
        ),
        (
            "Droit des affaires",
            "Business law",
            "قانون الأعمال",
            "Facture impayée : de la mise en demeure au jugement",
            "Unpaid invoice: from formal notice to judgment",
            "الفاتورة غير المدفوعة: من الإنذار إلى الحكم",
            "Les étapes du recouvrement d'une créance commerciale, amiable puis judiciaire.",
            "The stages of recovering a commercial debt, first amicably and then through the courts.",
            "مراحل تحصيل الدين التجاري ودياً ثم قضائياً.",
        ),
        (
            "Procédure",
            "Procedure",
            "الإجراءات",
            "Délais de recours : pourquoi chaque jour compte",
            "Appeal deadlines: why every day counts",
            "آجال الطعن: لماذا لكل يوم أهميته",
            "Appel, opposition, pourvoi : un recours formé hors délai est irrecevable.",
            "Appeals, objections and cassation: an out-of-time application may be inadmissible.",
            "الاستئناف والتعرض والنقض: قد لا يُقبل الطعن المقدم بعد انقضاء الأجل.",
        ),
    ]
    for position, values in enumerate(publications, start=1):
        Publication.objects.update_or_create(
            title_fr=values[3],
            defaults={
                "category_fr": values[0],
                "category_en": values[1],
                "category_ar": values[2],
                "title_en": values[4],
                "title_ar": values[5],
                "excerpt_fr": values[6],
                "excerpt_en": values[7],
                "excerpt_ar": values[8],
                "position": position,
                "is_active": True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("portal", "0002_galleryphoto_practicearea_publication_sitesettings_and_more")]
    operations = [migrations.RunPython(seed_public_site, migrations.RunPython.noop)]
