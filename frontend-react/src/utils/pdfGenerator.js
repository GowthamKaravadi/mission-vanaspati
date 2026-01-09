import jsPDF from 'jspdf';
import formatClassName from './formatClassName';

export const generateDiagnosisReport = (result, remedyInfo) => {
  const pdf = new jsPDF();
  
  // Set colors
  const primaryColor = [45, 106, 79]; // #2d6a4f
  const secondaryColor = [82, 183, 136]; // #52b788
  const textColor = [45, 55, 72]; // #2d3748
  
  // Title
  pdf.setFillColor(...primaryColor);
  pdf.rect(0, 0, 210, 40, 'F');
  pdf.setTextColor(255, 255, 255);
  pdf.setFontSize(24);
  pdf.setFont('helvetica', 'bold');
  pdf.text('Mission Vanaspati', 105, 20, { align: 'center' });
  pdf.setFontSize(14);
  pdf.text('Plant Disease Diagnosis Report', 105, 30, { align: 'center' });
  
  // Reset text color
  pdf.setTextColor(...textColor);
  
  // Date
  pdf.setFontSize(10);
  pdf.setFont('helvetica', 'normal');
  pdf.text(`Report Date: ${new Date().toLocaleDateString()}`, 20, 50);
  
  // Diagnosis Section
  pdf.setFontSize(16);
  pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(...primaryColor);
  pdf.text('Diagnosis', 20, 65);
  
  // Disease Name
  pdf.setFontSize(12);
  pdf.setTextColor(...textColor);
  const diseaseName = formatClassName(result.predicted_class || result.class);
  pdf.text(`Disease: ${diseaseName}`, 20, 75);
  
  // Confidence
  const confidence = (result.confidence * 100).toFixed(1);
  pdf.text(`Confidence Level: ${confidence}%`, 20, 83);
  
  // Confidence bar
  pdf.setFillColor(220, 220, 220);
  pdf.rect(20, 87, 170, 8, 'F');
  pdf.setFillColor(...secondaryColor);
  pdf.rect(20, 87, (170 * result.confidence), 8, 'F');
  
  // Description Section
  pdf.setFontSize(14);
  pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(...primaryColor);
  pdf.text('About This Condition', 20, 105);
  
  pdf.setFontSize(10);
  pdf.setFont('helvetica', 'normal');
  pdf.setTextColor(...textColor);
  const description = remedyInfo.description || 'No description available';
  const splitDescription = pdf.splitTextToSize(description, 170);
  pdf.text(splitDescription, 20, 113);
  
  // Remedies Section
  let yPos = 113 + (splitDescription.length * 5) + 10;
  
  pdf.setFontSize(14);
  pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(...primaryColor);
  pdf.text('Recommended Treatment Actions', 20, yPos);
  
  yPos += 10;
  pdf.setFontSize(10);
  pdf.setFont('helvetica', 'normal');
  pdf.setTextColor(...textColor);
  
  if (remedyInfo.remedies && remedyInfo.remedies.length > 0) {
    remedyInfo.remedies.forEach((remedy, index) => {
      if (yPos > 270) {
        pdf.addPage();
        yPos = 20;
      }
      
      pdf.setFillColor(...secondaryColor);
      pdf.circle(23, yPos - 1.5, 1.5, 'F');
      
      const splitRemedy = pdf.splitTextToSize(remedy, 160);
      pdf.text(splitRemedy, 28, yPos);
      yPos += (splitRemedy.length * 5) + 3;
    });
  }
  
  // Products Section
  if (remedyInfo.products && remedyInfo.products.length > 0) {
    yPos += 10;
    
    if (yPos > 250) {
      pdf.addPage();
      yPos = 20;
    }
    
    pdf.setFontSize(14);
    pdf.setFont('helvetica', 'bold');
    pdf.setTextColor(...primaryColor);
    pdf.text('Recommended Products', 20, yPos);
    
    yPos += 10;
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    pdf.setTextColor(...textColor);
    
    remedyInfo.products.forEach((product, index) => {
      if (yPos > 270) {
        pdf.addPage();
        yPos = 20;
      }
      
      pdf.setFont('helvetica', 'bold');
      pdf.text(`${index + 1}. ${product.name}`, 20, yPos);
      yPos += 5;
      
      pdf.setFont('helvetica', 'normal');
      pdf.setTextColor(100, 100, 100);
      pdf.text(`Type: ${product.type}`, 25, yPos);
      yPos += 5;
      
      pdf.setTextColor(45, 106, 79);
      pdf.textWithLink('View Product', 25, yPos, { url: product.link });
      pdf.setTextColor(...textColor);
      yPos += 8;
    });
  }
  
  // Alternative Predictions
  const alternatives = result.top_predictions || result.alternatives || [];
  if (alternatives.length > 0) {
    yPos += 10;
    
    if (yPos > 250) {
      pdf.addPage();
      yPos = 20;
    }
    
    pdf.setFontSize(14);
    pdf.setFont('helvetica', 'bold');
    pdf.setTextColor(...primaryColor);
    pdf.text('Alternative Diagnoses', 20, yPos);
    
    yPos += 10;
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    pdf.setTextColor(...textColor);
    
    alternatives.slice(0, 3).forEach((alt, index) => {
      if (yPos > 270) {
        pdf.addPage();
        yPos = 20;
      }
      
      const altClass = formatClassName(alt.class || alt.predicted_class);
      const altConfidence = (alt.confidence * 100).toFixed(1);
      pdf.text(`${index + 1}. ${altClass} (${altConfidence}%)`, 20, yPos);
      yPos += 6;
    });
  }
  
  // Footer
  const pageCount = pdf.internal.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    pdf.setPage(i);
    pdf.setFontSize(9);
    pdf.setTextColor(150, 150, 150);
    pdf.text(
      `Mission Vanaspati - Plant Disease Detection System | Page ${i} of ${pageCount}`,
      105,
      285,
      { align: 'center' }
    );
  }
  
  // Save PDF
  const filename = `diagnosis_${diseaseName}_${new Date().getTime()}.pdf`;
  pdf.save(filename);
};

export const generateBatchReport = (results, remedies) => {
  const pdf = new jsPDF();
  const primaryColor = [45, 106, 79];
  const textColor = [45, 55, 72];
  
  // Title page
  pdf.setFillColor(...primaryColor);
  pdf.rect(0, 0, 210, 50, 'F');
  pdf.setTextColor(255, 255, 255);
  pdf.setFontSize(28);
  pdf.setFont('helvetica', 'bold');
  pdf.text('Mission Vanaspati', 105, 25, { align: 'center' });
  pdf.setFontSize(16);
  pdf.text('Batch Diagnosis Report', 105, 38, { align: 'center' });
  
  pdf.setTextColor(...textColor);
  pdf.setFontSize(12);
  pdf.text(`Report Date: ${new Date().toLocaleDateString()}`, 105, 60, { align: 'center' });
  pdf.text(`Total Images Analyzed: ${results.length}`, 105, 68, { align: 'center' });
  
  // Add each result
  results.forEach((result, index) => {
    pdf.addPage();
    
    const className = result.predicted_class || result.class;
    const displayName = formatClassName(className);
    const remedyInfo = remedies[className] || { description: 'No information available', remedies: [] };
    
    // Result title
    pdf.setFontSize(16);
    pdf.setFont('helvetica', 'bold');
    pdf.setTextColor(...primaryColor);
    pdf.text(`Image ${index + 1}: ${displayName}`, 20, 20);
    
    pdf.setFontSize(10);
    pdf.setTextColor(...textColor);
    pdf.setFont('helvetica', 'normal');
    pdf.text(`Confidence: ${(result.confidence * 100).toFixed(1)}%`, 20, 30);
    
    // Description
    pdf.setFontSize(12);
    pdf.setFont('helvetica', 'bold');
    pdf.text('Description:', 20, 42);
    
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    const splitDesc = pdf.splitTextToSize(remedyInfo.description, 170);
    pdf.text(splitDesc, 20, 50);
    
    let yPos = 50 + (splitDesc.length * 5) + 8;
    
    // Remedies
    if (remedyInfo.remedies && remedyInfo.remedies.length > 0) {
      pdf.setFontSize(12);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Recommended Actions:', 20, yPos);
      
      yPos += 8;
      pdf.setFontSize(10);
      pdf.setFont('helvetica', 'normal');
      
      remedyInfo.remedies.forEach((remedy) => {
        const splitRemedy = pdf.splitTextToSize(`• ${remedy}`, 165);
        pdf.text(splitRemedy, 23, yPos);
        yPos += (splitRemedy.length * 5) + 2;
      });
    }
  });
  
  // Footer on all pages
  const pageCount = pdf.internal.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    pdf.setPage(i);
    pdf.setFontSize(9);
    pdf.setTextColor(150, 150, 150);
    pdf.text(
      `Mission Vanaspati - Batch Analysis Report | Page ${i} of ${pageCount}`,
      105,
      285,
      { align: 'center' }
    );
  }
  
  pdf.save(`batch_diagnosis_${new Date().getTime()}.pdf`);
};
