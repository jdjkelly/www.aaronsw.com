<xsl:stylesheet
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
  xmlns:xhtml="http://www.w3.org/1999/xhtml">
  
<xsl:template match="/">
   <rdf:RDF><rdf:Description rdf:about="">
      <xsl:apply-templates select="xhtml:html/xhtml:body/xhtml:ul/xhtml:li/xhtml:a"/>
   </rdf:Description></rdf:RDF>
</xsl:template>


<xsl:template match="xhtml:a">
<rdfs:seeAlso rdf:resource="{@href}" />   
</xsl:template>

<xsl:template match="*"/>

</xsl:stylesheet> 