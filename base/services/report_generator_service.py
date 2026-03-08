from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

class ReportGeneratorService:
    """Service pour générer les rapports exécutif et technique"""
    
    def generate_reports(self, analysis):
        """Génère les rapports exécutif et technique"""
        try:
            # Générer le rapport exécutif
            executive_report_content = self._generate_executive_report(analysis)
            
            # Générer le rapport technique
            technical_report_content = self._generate_technical_report(analysis)
            
            # Sauvegarder les rapports
            self._save_reports(analysis, executive_report_content, technical_report_content)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la génération des rapports: {str(e)}")
            return False
    
    def _generate_executive_report(self, analysis):
        """Génère le rapport exécutif avec SWOT et valeurs métiers"""
        try:
            context = {
                'analysis': analysis,
                'title': analysis.title,
                'organization': analysis.organization,
                'type': analysis.type,
                'context': analysis.context,
                'workshop1_data': analysis.workshop1_data,
                'workshop3_data': analysis.workshop3_data,
                'workshop5_data': analysis.workshop5_data,
            }
            
            # Extraire les données du workshop 1
            if analysis.workshop1_data:
                config = analysis.workshop1_data.get('config', {})
                context.update({
                    'valeurs_metier': config.get('valeursMetier', []),
                    'missions': config.get('missions', []),
                    'swot': config.get('analyseSWOT', {}),
                    'standard': config.get('standard', ''),
                })
            
            # Extraire les scénarios du workshop 3
            if analysis.workshop3_data:
                context['scenarios'] = analysis.workshop3_data.get('cartographie', {}).get('scenariosStrategiques', [])
            
            # Extraire les mesures du workshop 5
            if analysis.workshop5_data:
                context['security_measures'] = analysis.workshop5_data.get('securityMeasures', [])
            
            html_content = render_to_string('reports/executive_report.html', context)
            return html_content
        except Exception as e:
            print(f"Erreur lors de la génération du rapport exécutif: {str(e)}")
            raise
    
    def _generate_technical_report(self, analysis):
        """Génère le rapport technique avec tous les ateliers"""
        try:
            context = {
                'analysis': analysis,
                'title': analysis.title,
                'organization': analysis.organization,
                'type': analysis.type,
                'context': analysis.context,
                'workshop1_data': analysis.workshop1_data,
                'workshop2_data': analysis.workshop2_data,
                'workshop3_data': analysis.workshop3_data,
                'workshop4_data': analysis.workshop4_data,
                'workshop5_data': analysis.workshop5_data,
            }
            
            # Extraire les données du workshop 1
            if analysis.workshop1_data:
                config = analysis.workshop1_data.get('config', {})
                context.update({
                    'valeurs_metier': config.get('valeursMetier', []),
                    'missions': config.get('missions', []),
                    'swot': config.get('analyseSWOT', {}),
                    'standard': config.get('standard', ''),
                    'perimetre': config.get('perimetreEtude', ''),
                    'evenements_redoutes': config.get('evenementsRedoutes', ''),
                })
            
            # Extraire les données du workshop 2
            if analysis.workshop2_data:
                context.update({
                    'sources_risque': analysis.workshop2_data.get('sourcesRisque', []),
                    'objectifs_vises': analysis.workshop2_data.get('objectifsVises', []),
                })
            
            # Extraire les données du workshop 3
            if analysis.workshop3_data:
                cartographie = analysis.workshop3_data.get('cartographie', {})
                context.update({
                    'scenarios': cartographie.get('scenariosStrategiques', []),
                    'axes_attaque': cartographie.get('axesAttaquePrioritaires', []),
                })
            
            # Extraire les données du workshop 4
            if analysis.workshop4_data:
                context.update({
                    'supporting_assets': analysis.workshop4_data.get('supportingAssets', []),
                    'operational_scenarios': analysis.workshop4_data.get('operationalScenarios', []),
                })
            
            # Extraire les données du workshop 5
            if analysis.workshop5_data:
                context.update({
                    'security_measures': analysis.workshop5_data.get('securityMeasures', []),
                    'residual_risks': analysis.workshop5_data.get('residualRisks', []),
                })
            
            html_content = render_to_string('reports/technical_report.html', context)
            return html_content
        except Exception as e:
            print(f"Erreur lors de la génération du rapport technique: {str(e)}")
            raise
    
    def _save_reports(self, analysis, executive_html, technical_html):
        """Save reports as HTML files"""
        try:
            # Sauvegarder le rapport exécutif
            if executive_html:
                executive_filename = f'reports/executive_{analysis.slug}.html'
                analysis.executive_report.save(
                    executive_filename,
                    ContentFile(executive_html.encode('utf-8')),
                    save=False
                )
            
            # Sauvegarder le rapport technique
            if technical_html:
                technical_filename = f'reports/technical_{analysis.slug}.html'
                analysis.technical_report.save(
                    technical_filename,
                    ContentFile(technical_html.encode('utf-8')),
                    save=False
                )
            
            analysis.save(update_fields=['executive_report', 'technical_report'])
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des rapports: {str(e)}")
            raise
