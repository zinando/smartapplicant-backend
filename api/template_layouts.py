tp_layouts = {}
tp_layouts['ats_bold_classic_resume'] = {
                                        'education': {
                                            'template_anchor': '{{education_section}}',
                                            'item_template': [
                                                {
                                                    "type": "dated_line", 
                                                    "content": "{{degree}} in {{field_of_study}}",
                                                    "dates": "{{start_date}} - {{end_date}}",
                                                    "content_bold": True,
                                                    "new_paragraph": True
                                                },
                                                {"text": "{{institution}}, {{location}}", "italic": True, "new_paragraph": True},
                                                {"text": "{{description}}", "style": None, "new_paragraph": True}
                                            ],
                                            'separator': "\n"
                                        },
                                        'experience': {
                                            'template_anchor': '{{experience_section}}',
                                            'item_template': [
                                                {
                                                    "type": "dated_line",
                                                    "content": "{{position}}",
                                                    "dates": "{{start_date}} - {{end_date}}",
                                                    "content_bold": True,
                                                    "new_paragraph": True
                                                },
                                                {"text": "{{company}}", "italic": True, "new_paragraph": True},
                                                {
                                                    "text": "{{description}}", 
                                                    "bullet": False, 
                                                    "indent": 0, 
                                                    "new_paragraph": True,
                                                    "is_list": True,
                                                    "content_key": "description"
                                                },
                                                {"text": "Key Achievements:", "style": None, "new_paragraph": True, "content_bold": True},
                                                {
                                                    "text": "{{achievements}}", 
                                                    "bullet": True, 
                                                    "indent": 0.5, 
                                                    "new_paragraph": True,
                                                    "is_list": True,
                                                    "content_key": "achievements"
                                                }
                                            ],
                                            'separator': "\n"
                                        },
                                        'certifications': {
                                            'template_anchor': '{{certification_section}}',
                                            'item_template': [
                                                {
                                                    "type": "dated_line",
                                                    "content": "{{cert_name}} | {{cert_issuer}}",
                                                    "dates": "{{issue_date}}",
                                                    "content_bold": True,
                                                    "bullet": True, 
                                                    "indent": 0.5,
                                                    "new_paragraph": True
                                                }
                                            ],
                                            'separator': ""
                                        }
                                    }
tp_layouts['ats_bold_classic_resume_techpro'] = {
                                                    **tp_layouts['ats_bold_classic_resume'],
                                                    'project': {
                                                                    'template_anchor': '{{project_section}}',
                                                                    'item_template': [
                                                                        {
                                                                            "type": "dated_line",
                                                                            "content": "{{title}}",
                                                                            "dates": "{{date}}",
                                                                            "content_bold": True,
                                                                            "new_paragraph": True
                                                                        },
                                                                        {"text": "{{technologies}}", "italic": True, "new_paragraph": True},
                                                                        {
                                                                            "text": "{{description}}", 
                                                                            "bullet": True, 
                                                                            "indent": 0.5, 
                                                                            "new_paragraph": True,
                                                                            "is_list": True
                                                                        }
                                                                    ],
                                                                    'separator': "\n"
                                                                }
                                                }
tp_layouts['ats_bold_classic_resume_biz_and_finance'] = tp_layouts['ats_bold_classic_resume_techpro'].pop('project')
tp_layouts['ats_bold_classic_resume_healthcare_and_medical'] = {
                                                **tp_layouts['ats_bold_classic_resume'],
                                                'certifications': {
                                                    'template_anchor': '{{certification_section}}',
                                                    'item_template': [
                                                        {
                                                            "type": "dated_line",
                                                            "content": "{{cert_name}}",
                                                            "dates": "{{issue_date}}",
                                                            "content_bold": True,
                                                            "bullet": True, 
                                                            "indent": 0.5,
                                                            "new_paragraph": True
                                                        },
                                                        {"text": "{{cert_issuer}}", "italic": True, "new_paragraph": True, "indent": 0.5},
                                                    ],
                                                    'separator': ""
                                                }
                                            }

tp_layouts['ats_bold_classic_resume_education_and_training'] = {
                                                **tp_layouts["ats_bold_classic_resume_healthcare_and_medical"],
                                                'subjects': {
                                                    'template_anchor': '{{subject_section}}',
                                                    'item_template': [
                                                        {"text": "{{title}}", "content_bold": True, "new_paragraph": True},
                                                        {"text": "{{description}}", "italic": True, "new_paragraph": True, "indent": 0.5},
                                                    ],
                                                    'separator': ""
                                                }
                                            }
tp_layouts['ats_bold_classic_legal_and_government'] = {
                                        ** tp_layouts['ats_bold_classic_resume_healthcare_and_medical'],
                                        'publications': {
                                            'template_anchor': '{{publication_section}}',
                                            'item_template': [
                                                {
                                                    "type": "dated_line",
                                                    "content": "{{title}}",
                                                    "dates": "{{date}}",
                                                    "content_bold": True,
                                                    "bullet": False,
                                                    "new_paragraph": True
                                                },
                                                {"text": "{{source}}", "italic": True, "new_paragraph": True},
                                                {"text": "{{description}}", "italic": False, "new_paragraph": True, "bullet": True, "indent": 0.5}
                                            ],
                                            'separator': ""
                                        }
                                    }
tp_layouts['ats_bold_classic_resume_scinece_and_research'] = {
                                        **tp_layouts['ats_bold_classic_legal_and_government'],
                                        'research': {
                                            'template_anchor': '{{research_interest_section}}',
                                            'item_template': [
                                                {
                                                    "type": "dated_line",
                                                    "content": "{{title}}",
                                                    "dates": "{{date}}",
                                                    "content_bold": True,
                                                    "bullet": False,
                                                    "new_paragraph": True
                                                },
                                                {"text": "{{description}}", "italic": True, "new_paragraph": True, "bullet": True, "indent": 0.5}
                                            ],
                                            'separator': ""
                                        },
                                        'teaching': {
                                            'template_anchor': '{{teaching_section}}',
                                            'item_template': [
                                                {
                                                    "type": "dated_line",
                                                    "content": "{{institution}}",
                                                    "dates": "{{date}}",
                                                    "content_bold": True,
                                                    "bullet": False,
                                                    "new_paragraph": True
                                                },
                                                {"text": "{{role}} - {{subject}}", "italic": True, "new_paragraph": True},
                                                {"text": "{{description}}", "italic": False, "new_paragraph": True, "bullet": True, "indent": 0.5}
                                            ],
                                            'separator': ""
                                        }
}

tp_layouts['professional'] = tp_layouts['ats_bold_classic_resume']
tp_layouts['professional_premium'] = tp_layouts['ats_bold_classic_resume']
tp_layouts['professional_premium']['education']['item_template']=[
                                                {
                                                    "type": "dated_line", 
                                                    "content": "{{degree}} in {{field_of_study}}",
                                                    "dates": "{{graduation_date}}",
                                                    "content_bold": True,
                                                    "new_paragraph": True
                                                },
                                                {"text": "{{institution}}", "italic": True, "new_paragraph": True},
                                                {"text": "{{description}}", "style": None, "new_paragraph": True}
                                            ]
tp_layouts['modern'] =             {
                                        'education': {
                                            'template_anchor': '{{education_section}}',
                                            'item_template': [
                                                {
                                                    "type": "dated_line",
                                                    "content": "{{degree}}",
                                                    "dates": "{{graduation_date}}",
                                                    "content_bold": True,
                                                    "new_paragraph": True
                                                },
                                                {"text": "{{institution}}, {{location}}", "italic": True, "new_paragraph": True},
                                                {"text": "{{description}}", "style": None, "new_paragraph": True}
                                            ],
                                            'separator': "\n"
                                        },
                                        'experience': {
                                            'template_anchor': '{{experience_section}}',
                                            'item_template': [
                                                {
                                                    "type": "dated_line",
                                                    "content": "{{position}}",
                                                    "dates": "{{experience_duration}}",
                                                    "content_bold": True,
                                                    "new_paragraph": True
                                                },
                                                {"text": "{{company}}", "italic": True, "new_paragraph": True},
                                                {
                                                    "text": "{{description}}", 
                                                    "bullet": False, 
                                                    "indent": 0, 
                                                    "new_paragraph": True,
                                                    "is_list": True
                                                },
                                                {"text": "Key Achievements:", "style": None, "new_paragraph": True, "content_bold": True},
                                                {
                                                    "text": "{{achievements}}", 
                                                    "bullet": True, 
                                                    "indent": 0.5, 
                                                    "new_paragraph": True,
                                                    "is_list": True
                                                }
                                            ],
                                            'separator': "\n"
                                        },
                                        'certification': {
                                            'template_anchor': '{{certification_section}}',
                                            'item_template': [
                                                {
                                                    "text": "{{cert_name}}",
                                                    "content_bold": True,
                                                    "new_paragraph": True
                                                },
                                                {"text": "{{cert_issuer}}", "italic": False, "new_paragraph": True},
                                                {"text": "{{issue_date}}", "italic": True, "new_paragraph": True}
                                            ],
                                            'separator': ""
                                        },
                                        'project': {
                                            'template_anchor': '{{project_section}}',
                                            'item_template': [
                                                {
                                                    "type": "dated_line",
                                                    "content": "{{title}}",
                                                    "dates": "{{date}}",
                                                    "content_bold": True,
                                                    "new_paragraph": True
                                                },
                                                {"text": "{{technologies}}", "italic": True, "new_paragraph": True},
                                                {
                                                    "text": "{{description}}", 
                                                    "bullet": True, 
                                                    "indent": 0.5, 
                                                    "new_paragraph": True,
                                                    "is_list": True
                                                }
                                            ],
                                            'separator': "\n"
                                        },
                                        'skills': {
                                            'template_anchor': '{{skills_section}}',
                                            'item_template': [
                                                {"text": "{{skill}}", "new_paragraph": True, 'bullet': True, 'indent': 0.5, 'is_list': True}
                                            ],
                                            'separator': ""
                                        }
                                    }
tp_layouts['modern_premium'] = {
                                **tp_layouts['modern'],
                                'certifications': {
                                            'template_anchor': '{{certification_section}}',
                                            'item_template': [
                                                {
                                                    "text": "{{cert_name}}",
                                                    "content_bold": True,
                                                    "new_paragraph": True
                                                },
                                                {"text": "{{cert_issuer}}", "italic": False, "new_paragraph": True},
                                                {"text": "{{issue_date}}", "italic": True, "new_paragraph": True}
                                            ],
                                            'separator': ""
                                        },
                                'experience_continuation': {
                                            'template_anchor': '{{experience_section_continuation}}',
                                            'item_template': [
                                                {
                                                    "type": "dated_line",
                                                    "content": "{{position}}",
                                                    "dates": "{{experience_duration}}",
                                                    "content_bold": True,
                                                    "new_paragraph": True
                                                },
                                                {"text": "{{company}}", "italic": True, "new_paragraph": True},
                                                {
                                                    "text": "{{description}}", 
                                                    "bullet": False, 
                                                    "indent": 0, 
                                                    "new_paragraph": True,
                                                    "is_list": True
                                                },
                                                {"text": "Key Achievements:", "style": None, "new_paragraph": True, "content_bold": True},
                                                {
                                                    "text": "{{achievements}}", 
                                                    "bullet": True, 
                                                    "indent": 0.5, 
                                                    "new_paragraph": True,
                                                    "is_list": True
                                                }
                                            ],
                                            'separator': "\n"
                                        },
}