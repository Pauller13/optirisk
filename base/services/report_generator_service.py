from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from io import BytesIO
import os
from dotenv import load_dotenv
from xhtml2pdf import pisa
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class ReportGeneratorService:
    """Service pour générer les rapports exécutif et technique en PDF"""
    
    def generate_reports(self, analysis):
        """Génère les rapports exécutif et technique en PDF"""
        try:
            # Générer le rapport exécutif
            executive_report_pdf = self._generate_executive_report(analysis)
            
            # Générer le rapport technique
            technical_report_pdf = self._generate_technical_report(analysis)
            
            # Sauvegarder les rapports
            self._save_reports(analysis, executive_report_pdf, technical_report_pdf)
            
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la génération des rapports: {str(e)}", exc_info=True)
            print(f"Erreur lors de la génération des rapports: {str(e)}")
            return False
    
    def _generate_executive_report(self, analysis):
        """Génère le rapport exécutif avec SWOT et valeurs métiers"""
        try:
            context = self._prepare_executive_context(analysis)
            html_content = render_to_string('reports/executive_report.html', context)
            
            # Convertir HTML en PDF
            pdf_content = self._html_to_pdf(html_content)
            return pdf_content
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport exécutif: {str(e)}", exc_info=True)
            print(f"Erreur lors de la génération du rapport exécutif: {str(e)}")
            raise
    
    def _prepare_executive_context(self, analysis):
        """Prépare le contexte pour le rapport exécutif"""
        context = {
            'analysis': analysis,
            'now': analysis.created_at,
        }
        
        # Structurer workshop1 avec sa config
        if analysis.workshop1_data:
            context['workshop1'] = {
                'config': analysis.workshop1_data.get('config', {})
            }
        
        # Structurer workshop3 avec cartographie
        if analysis.workshop3_data:
            context['workshop3'] = {
                'cartographie': analysis.workshop3_data.get('cartographie', {})
            }
        
        # Structurer workshop5 avec mesures
        if analysis.workshop5_data:
            context['workshop5'] = analysis.workshop5_data
        
        return context
    
    def _generate_technical_report(self, analysis):
        """Génère le rapport technique avec tous les ateliers"""
        try:
            context = self._prepare_technical_context(analysis)
            html_content = render_to_string('reports/technical_report.html', context)
            
            # Convertir HTML en PDF
            pdf_content = self._html_to_pdf(html_content)
            return pdf_content
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport technique: {str(e)}", exc_info=True)
            print(f"Erreur lors de la génération du rapport technique: {str(e)}")
            raise
    
    def _prepare_technical_context(self, analysis):
        """Prépare le contexte pour le rapport technique"""
        context = {
            'analysis': analysis,
            'now': analysis.created_at,
        }
        
        # Structurer workshop1 avec sa config
        if analysis.workshop1_data:
            context['workshop1'] = {
                'config': analysis.workshop1_data.get('config', {})
            }
        
        # Structurer workshop2
        if analysis.workshop2_data:
            context['workshop2'] = {
                'sourcesRisque': analysis.workshop2_data.get('sourcesRisque', []),
                'objectifsVises': analysis.workshop2_data.get('objectifsVises', [])
            }
        
        # Structurer workshop3 avec cartographie
        if analysis.workshop3_data:
            context['workshop3'] = {
                'cartographie': analysis.workshop3_data.get('cartographie', {})
            }
        
        # Structurer workshop4 avec assets
        if analysis.workshop4_data:
            context['workshop4'] = {
                'supportingAssets': analysis.workshop4_data.get('supportingAssets', []),
                'operationalScenarios': analysis.workshop4_data.get('operationalScenarios', [])
            }
        
        # Structurer workshop5 avec mesures et risques
        if analysis.workshop5_data:
            context['workshop5'] = {
                'securityMeasures': analysis.workshop5_data.get('securityMeasures', []),
                'residualRisks': analysis.workshop5_data.get('residualRisks', [])
            }
        
        return context
    
    def _html_to_pdf(self, html_content):
        """Convertit le contenu HTML en PDF"""
        try:
            # Créer un BytesIO pour stocker le PDF
            pdf_buffer = BytesIO()
            
            # Convertir HTML en PDF avec xhtml2pdf
            pisa_status = pisa.CreatePDF(
                BytesIO(html_content.encode('utf-8')),
                pdf_buffer,
                encoding='UTF-8'
            )
            
            if pisa_status.err:
                raise Exception(f"Erreur lors de la génération du PDF: {pisa_status.err}")
            
            pdf_buffer.seek(0)
            return pdf_buffer.getvalue()
        except Exception as e:
            logger.error(f"Erreur lors de la conversion HTML en PDF: {str(e)}", exc_info=True)
            print(f"Erreur lors de la conversion HTML en PDF: {str(e)}")
            raise
    
    def _save_reports(self, analysis, executive_pdf, technical_pdf):
        """Save reports as PDF files"""
        try:
            # Sauvegarder le rapport exécutif
            if executive_pdf:
                executive_filename = f'reports/executive_{analysis.slug}.pdf'
                analysis.executive_report.save(
                    executive_filename,
                    ContentFile(executive_pdf),
                    save=False
                )
                logger.info(f"Rapport exécutif sauvegardé: {executive_filename}")
            
            # Sauvegarder le rapport technique
            if technical_pdf:
                technical_filename = f'reports/technical_{analysis.slug}.pdf'
                analysis.technical_report.save(
                    technical_filename,
                    ContentFile(technical_pdf),
                    save=False
                )
                logger.info(f"Rapport technique sauvegardé: {technical_filename}")
            
            analysis.save(update_fields=['executive_report', 'technical_report'])
            logger.info(f"Rapports sauvegardés avec succès pour l'analyse: {analysis.id}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des rapports: {str(e)}", exc_info=True)
            print(f"Erreur lors de la sauvegarde des rapports: {str(e)}")
            raise
