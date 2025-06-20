tp_layouts = {}
tp_layouts['ats_bold_classic_resume'] = {
                                        'education': {
                                            'template_placeholder': '{{education_section}}',
                                            'item_template': [
                                                {
                                                    "type": "dated_line",
                                                    "content": "{{degree}} in {{field_of_study}}",
                                                    "dates": "{{start_date}} - {{end_date}}",
                                                    "content_bold": True,
                                                    "new_paragraph": True
                                                },
                                                {"text": "{{institution}}", "italic": True, "new_paragraph": True},
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
                                                {"text": "Key Responsibilities / Achievements:", "style": None, "new_paragraph": True},
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
                                                                    'template_placeholder': '{{project_section}}',
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