import json
from django.core.management.base import BaseCommand
from django.utils import timezone
import os
from datetime import datetime
from api.models import (
    Skill, JobTitle, Country, State, City, Institution, 
    Certification, FieldOfStudy, Degree, ExperienceDescription,
    ExperienceAchievement, Industry, Company, ProfessionalRelationship,
    Application, Technology, Location, Responsibility
)
from api.suggestion_resource import (COUNTRY_OPTIONS, STATE_OPTIONS, CITIES_DATA,
                                     LOCATION_DATA, SKILLS_DATA, INDUSTRY_DATA, FOS, DEGREES,
                                     PROFESSIONAL_RELATIONSHIPS, TECHNOLOGIES, APPLICATIONS,
                                     CERTIFICATIONS, INSTITUTIONS, COMPANIES, RESPONSIBILITIES)


class Command(BaseCommand):
    help = 'Seed the database with initial suggestion data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Seeding suggestion data...'))
        
        # Run all seeders
        # self.seed_countries()
        # self.seed_states()
        # self.seed_cities()
        # self.seed_locations()
        # self.seed_skills()
        # self.seed_industries()
        # self.seed_professional_relationships()
        # self.seed_technologies()
        # self.seed_applications()
        # self.seed_fields_of_study()
        # self.seed_degrees()
        # self.seed_job_titles()
        # self.seed_certifications()
        self.seed_experience_descriptions()
        # self.seed_experience_achievements()
        # self.seed_institutions()
        # self.seed_companies()
        
        self.stdout.write(self.style.SUCCESS('✅ Seeding complete!'))

    # ============================================
    # COUNTRY SEEDER
    # ============================================
    def seed_countries(self):
        countries = COUNTRY_OPTIONS
        
        for data in countries:
            obj, created = Country.objects.get_or_create(
                country_code=data['code'],
                defaults={'name': data['name'], 'capital': data['capital']}
            )
            if created:
                self.stdout.write(f'  ✅ Created country: {obj.name}')
        
        self.stdout.write(self.style.SUCCESS(f'  📍 {Country.objects.count()} countries seeded'))

    # ============================================
    # STATE SEEDER
    # ============================================
    def seed_states(self):
        # isolate countries that have been seeded and aggregate all the States to be processed
        countries = Country.objects.all()
        states_to_process = []
        for country in STATE_OPTIONS:
            if not country.get('seeded'):
                country_obj = countries.filter(country_code=country['code']).first()
                if country_obj and country.get('states') and len(country.get('states')) > 0:
                    for state in  country.get('states'):
                        states_to_process.append({
                            'name': state['name'],
                            'capital': state['capital'],
                            'country': country_obj
                        })
        
        # add all states to be processed
        if len(states_to_process) > 0:
            for state in states_to_process:               
                obj, created = State.objects.get_or_create(
                    name= state['name'],
                    country= state['country'],
                    defaults= {'capital':state['capital']}
                )
                if created:
                    self.stdout.write(f'  ✅ Created state: {obj.name}, {obj.country.name}')
                
        self.stdout.write(self.style.SUCCESS(f'  📍 {State.objects.count()} states seeded'))

    # ============================================
    # CITY SEEDER
    # ============================================
    def seed_cities(self):    
        # Create a logs directory if it doesn't exist
        logs_dir = 'seed_logs'
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        multi_match = []
        no_match = []
        to_process = []
        null_match = []
        
        for citi in CITIES_DATA:
            if citi.get('state_name', None) and citi.get('country_code', None):                
                state_name = citi.get('state_name')
                country_code = citi.get('country_code')
                country = Country.objects.filter(country_code=country_code).first()
                state = State.objects.filter(
                    name__iexact=state_name,
                    country=country,
                    is_active=True
                ).first()
                if not state:
                    null_match.append({
                        'citi_data': citi,
                        'country': country.name if country else None,
                        'state': state
                    })
                    continue
                for city_name in citi['cities']:
                    to_process.append({
                        'state': state,
                        'city': city_name.strip()
                    })
                continue
            else:
                # continue
                state_name = citi['state'].strip()
                state_match = State.objects.filter(
                    name__iexact=state_name,
                    is_active=True
                ).all()
                
                
                if len(state_match) > 0:
                    if len(state_match) > 1:
                        # Record which countries these states belong to
                        countries = [s.country.country_code for s in state_match]
                        multi_match.append({
                            'state_name': state_name,
                            'countries': countries,
                            'cities': citi['cities']
                        })
                        continue
                    state = state_match[0]
                    for city_name in citi['cities']:
                        to_process.append({
                            'state': state,
                            'city': city_name.strip()
                        })
                else:
                    no_match.append({
                        'state_name': state_name,
                        'cities': citi['cities']
                    })
                    continue
        
        # Create cities
        if len(to_process) > 0:
            for citi in to_process:
                city_obj, created = City.objects.get_or_create(
                    state=citi['state'],
                    name=citi['city']
                )
                if created:
                    self.stdout.write(f'  ✅ Created city: {city_obj.name}, {city_obj.state.name}, {city_obj.state.country.name}')
        
        # ============================================
        # SAVE MULTI_MATCH AND NO_MATCH TO FILES
        # ============================================
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        
        if multi_match:
            multi_match_file = os.path.join(logs_dir, f'multi_match_states_{timestamp}.json')
            with open(multi_match_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'count': len(multi_match),
                    'items': multi_match,
                    'note': 'These state names have multiple matches in the database across different countries.',
                    'action_required': 'Please add state codes or country codes to disambiguate.'
                }, f, indent=2, ensure_ascii=False)
            self.stdout.write(self.style.WARNING(f'  ⚠️ {len(multi_match)} states with multiple matches saved to: {multi_match_file}'))
        
        if no_match:
            no_match_file = os.path.join(logs_dir, f'no_match_states_{timestamp}.json')
            with open(no_match_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'count': len(no_match),
                    'items': no_match,
                    'note': 'These state names were not found in the database.',
                    'action_required': 'Please review and add these states or correct the city data.'
                }, f, indent=2, ensure_ascii=False)
            self.stdout.write(self.style.WARNING(f'  ⚠️ {len(no_match)} states with no matches saved to: {no_match_file}'))
        
        # ============================================
        # SUMMARY
        # ============================================
        self.stdout.write(self.style.SUCCESS(f'\n  📊 Summary:'))
        self.stdout.write(self.style.SUCCESS(f'     ✅ Cities created: {len(to_process)}'))
        self.stdout.write(self.style.WARNING(f'     ⚠️  Multi-match states: {len(multi_match)}'))
        self.stdout.write(self.style.WARNING(f'     ⚠️  Null-match states: {null_match}'))
        self.stdout.write(self.style.WARNING(f'     ⚠️  No-match states: {len(no_match)}'))
        self.stdout.write(self.style.SUCCESS(f'  📍 Total cities in database: {City.objects.count()}'))

    # ============================================
    # LOCATION SEEDER
    # ============================================
    def seed_locations(self):
        logs_dir = 'seed_logs'
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        no_match = []
        to_process = []

        for data in LOCATION_DATA:
            country = Country.objects.filter(country_code=data['country_code'].strip()).first()
            state = State.objects.filter(country=country, capital__iexact=data['state_capital'].strip()).first()
            city = City.objects.filter(state=state, name__iexact=data['city_name'].strip()).first()            
            if country and state and city:
                for location in data['locations']:
                    # loc = Location.objects.filter(name__iexact=location)
                    # if not loc:
                    to_process.append({
                        'location_name': location.strip(),
                        'city': city
                    })
            else:
                no_match.append({
                    'location_data': data,
                    'matched_country': f'{country}',
                    'matched_state': f'{state}',
                    'matched_city': f'{city}' 
                })
        
        for data in to_process:
            try:                
                obj, created = Location.objects.get_or_create(
                    name=data['location_name'],
                    city=data['city']
                )
                if created:
                    self.stdout.write(f'  ✅ Created location: {obj.name}, {obj.city.name}, {obj.city.state.name}, {obj.city.state.country.name}')
            except City.DoesNotExist:
                self.stdout.write(f'  ⚠️ City not found for: {data["city"]}')
        
        if no_match:
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            no_match_file = os.path.join(logs_dir, f'no_match_states_{timestamp}.json')
            with open(no_match_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'count': len(no_match),
                    'items': no_match,
                    'note': 'These state names were not found in the database.',
                    'action_required': 'Please review and add these states or correct the city data.'
                }, f, indent=2, ensure_ascii=False)
            self.stdout.write(self.style.WARNING(f'  ⚠️ {len(no_match)} states with no matches saved to: {no_match_file}'))
        
        # ============================================
        # SUMMARY
        # ============================================
        self.stdout.write(self.style.SUCCESS(f'\n  📊 Summary:'))
        self.stdout.write(self.style.SUCCESS(f'     ✅ Locations created: {len(to_process)}'))
        self.stdout.write(self.style.WARNING(f'     ⚠️  No-match data: {len(no_match)}'))
        self.stdout.write(self.style.SUCCESS(f'  📍 {Location.objects.count()} locations seeded'))

    # ============================================
    # SKILL SEEDER
    # ============================================
    def seed_skills(self):
        skills = SKILLS_DATA
        
        for data in skills:
            obj, created = Skill.objects.get_or_create(
                name=data['name'].strip(),
                defaults={'category': data['category'].strip()}
            )
            if created:
                self.stdout.write(f'  ✅ Created skill: {obj.name} ({obj.get_category_display()})')
            else:
                if not obj.category:
                    obj.category = data['category'].strip()
                    obj.save(update_fields=['category'])
                    self.stdout.write(f'  ⚠️ Updated skill: {obj.name} ({obj.get_category_display()})')
        
        self.stdout.write(self.style.SUCCESS(f'  🛠️ {Skill.objects.count()} skills seeded'))

    # ============================================
    # INDUSTRY SEEDER
    # ============================================
    def seed_industries(self):
        industries = INDUSTRY_DATA
        job_title_list = []
        
        for data in industries:
            obj, created = Industry.objects.get_or_create(title=data['name'])
            if created:
                self.stdout.write(f'  ✅ Created industry: {obj.title}')
            
            for title in data['titles']:
                job_title_list.append({
                    'title': title.strip(),
                    'industry': obj
                })
        
        for data in job_title_list:
            jt_obj, created = JobTitle.objects.get_or_create(
                title=data['title']
            )
            if created:
                self.stdout.write(f'  ✅ Created job_title: {jt_obj.title}')
            
            industry = data['industry']
            if industry:
                industry.job_titles.add(jt_obj)
                self.stdout.write(f'  ✅ Added {jt_obj.title} to {industry.title}')

        self.stdout.write(self.style.SUCCESS(f'  🏭 {Industry.objects.count()} industries seeded'))

    # ============================================
    # PROFESSIONAL RELATIONSHIP SEEDER
    # ============================================
    def seed_professional_relationships(self):
        relationships = PROFESSIONAL_RELATIONSHIPS
        
        for title in relationships:
            obj, created = ProfessionalRelationship.objects.get_or_create(title=title)
            if created:
                self.stdout.write(f'  ✅ Created relationship: {obj.title}')
        
        self.stdout.write(self.style.SUCCESS(f'  🤝 {ProfessionalRelationship.objects.count()} relationships seeded'))

    # ============================================
    # TECHNOLOGY SEEDER
    # ============================================
    def seed_technologies(self):
        technologies = TECHNOLOGIES
        
        for data in technologies:
            obj, created = Technology.objects.get_or_create(
                name=data['name'],
                category= data['category'],
                defaults={'category': data['category']}
            )
            if created:
                self.stdout.write(f'  ✅ Created technology: {obj.name} ({obj.get_category_display()})')
        
        self.stdout.write(self.style.SUCCESS(f'  💻 {Technology.objects.count()} technologies seeded'))

    # ============================================
    # APPLICATION SEEDER
    # ============================================
    def seed_applications(self):
        applications = APPLICATIONS
        technology_list = []
        
        for data in applications:
            obj, created = Application.objects.get_or_create(
                title=data['name'],
                defaults={'title': data['name']}
            )
            if created:
                self.stdout.write(f'  ✅ Created application: {obj.title}.')
            
            mylist = [{'application':obj, 'technology': tech} for tech in data['technologies']]
            technology_list.extend(mylist)
        
        for technology in technology_list:
            # tech_obj, created = Technology.objects.get_or_create(
            #     name=technology['technology'],
            #     defaults={'category': 'other'}
            # )
            # if created:
            #     self.stdout.write(f'  ✅ Created new technology: {tech_obj.name} ({tech_obj.get_category_display()})')
            
            existing = Technology.objects.filter(name=technology['technology']) # we use this because we know the lookup can match multiple objs

            if existing.exists():
                tech_objs = list(existing)
                created = False
            else:
                tech_objs = [Technology.objects.create(
                    name=technology['technology'],
                    category='other'
                )]
                created = True
            if created:
                self.stdout.write(f'  ✅ Created new technology: {tech_obj.name} ({tech_obj.get_category_display()})')
            

            for tech_obj in tech_objs:
                # if not tech_obj.applications.contains(technology['application']):
                tech_obj.applications.add(technology['application'])  # this operation is idempotent, reason the step above isn't necessary
                self.stdout.write(f'  ✅ Added {technology["application"].title} to {tech_obj.name}.')
        
        self.stdout.write(self.style.SUCCESS(f'  📱 {Application.objects.count()} applications seeded'))

    # ============================================
    # FIELD OF STUDY SEEDER
    # ============================================
    def seed_fields_of_study(self):
        fields = FOS
        
        for name in fields:
            obj, created = FieldOfStudy.objects.get_or_create(title=name)
            if created:
                self.stdout.write(f'  ✅ Created field of study: {obj.title}')
        
        self.stdout.write(self.style.SUCCESS(f'  📚 {FieldOfStudy.objects.count()} fields of study seeded'))

    # ============================================
    # DEGREE SEEDER
    # ============================================
    def seed_degrees(self):
        degrees = DEGREES

        degree_list = []
        
        for data in degrees:             
            obj, created = Degree.objects.get_or_create(
                title=data['title'],
                defaults={'abbr': data['abbr']}
            )
            if created:
                self.stdout.write(f'  ✅ Created degree: {obj.title}.')
            my_list = [{'degree': obj, 'fos': fos.strip()} for fos in data['fields']]
            degree_list.extend(my_list)
        
        for degree in degree_list:
            fos_obj, created = FieldOfStudy.objects.get_or_create(
                title = degree['fos']
            )

            if created:
                self.stdout.write(f'Created new FOS: {fos_obj.title}.')
            
            degree_obj: Degree = degree['degree']
            degree_obj.fields_of_study.add(fos_obj)
            self.stdout.write(f'  ✅ Added {fos_obj.title} to {degree_obj.title}.')

           
        self.stdout.write(self.style.SUCCESS(f'  🎓 {Degree.objects.count()} degrees seeded'))

    # ============================================
    # JOB TITLE SEEDER
    # ============================================
    def seed_job_titles(self):
        # This will be populated with many job titles
        # We'll add basic ones here, AI will generate more
        job_titles = [
            {'title': 'Software Engineer', 'group': 'Technology & Engineering'},
            {'title': 'Senior Software Engineer', 'group': 'Technology & Engineering'},
            {'title': 'Full Stack Developer', 'group': 'Technology & Engineering'},
            {'title': 'Frontend Developer', 'group': 'Technology & Engineering'},
            {'title': 'Backend Developer', 'group': 'Technology & Engineering'},
            {'title': 'DevOps Engineer', 'group': 'Technology & Engineering'},
            {'title': 'Data Scientist', 'group': 'Science & Research'},
            {'title': 'Machine Learning Engineer', 'group': 'Science & Research'},
            {'title': 'Data Analyst', 'group': 'Science & Research'},
            {'title': 'Product Manager', 'group': 'Business & Finance'},
            {'title': 'Project Manager', 'group': 'Business & Finance'},
            {'title': 'UX Designer', 'group': 'Creative & Design'},
            {'title': 'UI Designer', 'group': 'Creative & Design'},
            {'title': 'Marketing Manager', 'group': 'Sales & Marketing'},
            {'title': 'Sales Director', 'group': 'Sales & Marketing'},
            {'title': 'Business Analyst', 'group': 'Business & Finance'},
            {'title': 'Systems Administrator', 'group': 'Technology & Engineering'},
            {'title': 'Network Engineer', 'group': 'Technology & Engineering'},
            {'title': 'Security Analyst', 'group': 'Technology & Engineering'},
            {'title': 'QA Engineer', 'group': 'Technology & Engineering'},
            {'title': 'Cloud Architect', 'group': 'Technology & Engineering'},
            {'title': 'Solutions Architect', 'group': 'Technology & Engineering'},
            {'title': 'Engineering Manager', 'group': 'Technology & Engineering'},
            {'title': 'IT Director', 'group': 'Technology & Engineering'},
            {'title': 'CTO', 'group': 'Technology & Engineering'},
            {'title': 'Product Designer', 'group': 'Creative & Design'},
            {'title': 'Graphic Designer', 'group': 'Creative & Design'},
            {'title': 'Accountant', 'group': 'Business & Finance'},
            {'title': 'Financial Analyst', 'group': 'Business & Finance'},
            {'title': 'Investment Banker', 'group': 'Business & Finance'},
            {'title': 'Nurse', 'group': 'Healthcare & Medical'},
            {'title': 'Physician', 'group': 'Healthcare & Medical'},
            {'title': 'Pharmacist', 'group': 'Healthcare & Medical'},
            {'title': 'Teacher', 'group': 'Education & Training'},
            {'title': 'Professor', 'group': 'Education & Training'},
            {'title': 'Lecturer', 'group': 'Education & Training'},
            {'title': 'Lawyer', 'group': 'Legal & Government'},
            {'title': 'Paralegal', 'group': 'Legal & Government'},
            {'title': 'Judge', 'group': 'Legal & Government'},
            {'title': 'Architect', 'group': 'Construction & Real Estate'},
            {'title': 'Civil Engineer', 'group': 'Construction & Real Estate'},
            {'title': 'Construction Manager', 'group': 'Construction & Real Estate'},
        ]
        
        for data in job_titles:
            obj, created = JobTitle.objects.get_or_create(
                title=data['title'],
                defaults={'field_group': data['group']}
            )
            if created:
                self.stdout.write(f'  ✅ Created job title: {obj.title} ({obj.field_group})')
        
        self.stdout.write(self.style.SUCCESS(f'  💼 {JobTitle.objects.count()} job titles seeded'))

    # ============================================
    # CERTIFICATION SEEDER
    # ============================================
    def seed_certifications(self):
        certifications = CERTIFICATIONS
        title_list = []
        
        for data in certifications:
            obj, created = Certification.objects.get_or_create(
                name=data['name'],
                defaults={'issuer': data['issuer']}
            )
            if created:
                self.stdout.write(f'  ✅ Created certification: {obj.name} ({obj.issuer})')

            mylist = [{'certification': obj, 'title': title} for title in data['titles']]
            title_list.extend(mylist)
        
        for data in title_list:
            jt_obj, created = JobTitle.objects.get_or_create(
                title=data['title']
            )
            if created:
                self.stdout.write(f'Created new job title: {jt_obj.title}.')
            
            cert: Certification = data['certification']
            cert.job_titles.add(jt_obj)
            self.stdout.write(f'  ✅ Added {jt_obj.title} to {cert.name}.')
        
        self.stdout.write(self.style.SUCCESS(f'  📜 {Certification.objects.count()} certifications seeded'))

    # ============================================
    # INSTITUTION SEEDER
    # ============================================
    def seed_institutions(self):
        institutions = INSTITUTIONS
        
        for data in institutions:
            try:
                country = Country.objects.get(country_code=data['country'])
                obj, created = Institution.objects.get_or_create(
                    name=data['name'],
                    country=country
                )
                if created:
                    self.stdout.write(f'  ✅ Created institution: {obj.name} ({obj.country.name})')
            except Country.DoesNotExist:
                self.stdout.write(f'  ⚠️ Country not found: {data["country"]}')
        
        self.stdout.write(self.style.SUCCESS(f'  🏫 {Institution.objects.count()} institutions seeded'))

    # ============================================
    # COMPANY SEEDER
    # ============================================
    def seed_companies(self):
        companies = COMPANIES
        
        for data in companies:
            try:
                country = Country.objects.get(country_code=data['country'])
                obj, created = Company.objects.get_or_create(
                    name=data['name'],
                    country=country
                )
                if created:
                    self.stdout.write(f'  ✅ Created company: {obj.name} ({obj.country.name})')
            except Country.DoesNotExist:
                self.stdout.write(f'  ⚠️ Country not found: {data["country"]}')
        
        self.stdout.write(self.style.SUCCESS(f'  🏢 {Company.objects.count()} companies seeded'))

    # ============================================
    # EXPERIENCE DESCRIPTION SEEDER
    # ============================================
    def seed_experience_descriptions(self):
        descriptions = RESPONSIBILITIES
        resps = Responsibility.objects.all()
        for resp in resps:
            # if resp
            desc_obj, created = ExperienceDescription.objects.get_or_create(
                description = resp.text.strip()
            )
            if created:
                self.stdout.write(f'  ✅ Created: {desc_obj.description}')
            desc_obj.job_titles.set(resp.jobs.all())
            titles = [x for x  in resp.jobs.all()]
            self.stdout.write(f'  Added: {titles} to the description above.')
        
                
        to_process = []

        for data in descriptions:
            try:
                job = JobTitle.objects.get(title=data['title'])
                for x in range(len(data['job_descriptions'])):
                    description: str = data['job_descriptions'][x]
                    achievement: str = data['achievements'][x]
                    to_process.append({
                        'title': job,
                        'description': description.strip(),
                        'achievement': achievement.strip()
                    })
            except JobTitle.DoesNotExist:
                self.stdout.write(f'  ⚠️ Job title not found: {data["job_title"]}')
        
        for data in to_process:
            desc_obj, created = ExperienceDescription.objects.get_or_create(
                description=data['description']
            )
            if created:
                self.stdout.write(f'  ✅ Created: {desc_obj.description}')
            
            desc_obj.job_titles.add(data['title'])

            ach_obj, created = ExperienceAchievement.objects.get_or_create(
                achievement=data['achievement'],
                description=desc_obj,
                job_title=data['title']
            )

            if created:
                self.stdout.write(f'Also created achievement: {ach_obj.achievement}') 

        no_jts = []
        jts = JobTitle.objects.all()
        for jt in jts:
            if not jt.experience_descriptions.exists():
                no_jts.append(jt.title)
        
        self.stdout.write(f'Jobtitles without job descriptions: \n\n{no_jts}\n\n')
        
        self.stdout.write(self.style.SUCCESS(f'  📝 {ExperienceDescription.objects.count()} experience descriptions seeded'))

    # ============================================
    # EXPERIENCE ACHIEVEMENT SEEDER
    # ============================================
    def seed_experience_achievementsxxx(self):
        achievements = [
            {'achievement': 'Increased application performance by 40% through optimization', 'job_title': 'Software Engineer'},
            {'achievement': 'Led a team of 5 developers to deliver a major product feature', 'job_title': 'Software Engineer'},
            {'achievement': 'Reduced deployment time by 60% with CI/CD automation', 'job_title': 'DevOps Engineer'},
            {'achievement': 'Improved customer satisfaction scores by 25% with UX redesign', 'job_title': 'UX Designer'},
            {'achievement': 'Saved $500,000 annually through infrastructure optimization', 'job_title': 'Cloud Architect'},
            {'achievement': 'Increased revenue by 15% through data-driven product decisions', 'job_title': 'Product Manager'},
            {'achievement': 'Delivered project 2 months ahead of schedule', 'job_title': 'Project Manager'},
            {'achievement': 'Improved model accuracy by 12% with feature engineering', 'job_title': 'Data Scientist'},
            {'achievement': 'Reduced cloud costs by 30% through resource optimization', 'job_title': 'DevOps Engineer'},
            {'achievement': 'Scaled application to support 10 million users', 'job_title': 'Software Engineer'},
        ]
        
        for data in achievements:
            try:
                job = JobTitle.objects.get(title=data['job_title'])
                # Find a description for this job or create one
                desc = ExperienceDescription.objects.filter(job_title=job).first()
                if not desc:
                    desc = ExperienceDescription.objects.create(
                        description=f'General responsibilities for {job.title}',
                        job_title=job
                    )
                obj, created = ExperienceAchievement.objects.get_or_create(
                    achievement=data['achievement'],
                    description=desc,
                    defaults={'job_title': job}
                )
                if created:
                    self.stdout.write(f'  ✅ Created achievement for: {job.title}')
            except JobTitle.DoesNotExist:
                self.stdout.write(f'  ⚠️ Job title not found: {data["job_title"]}')
        
        self.stdout.write(self.style.SUCCESS(f'  🏆 {ExperienceAchievement.objects.count()} achievements seeded'))