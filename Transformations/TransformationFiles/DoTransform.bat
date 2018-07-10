@echo off

RaptorXML xslt --xslt-version=1 --input="OED_SourceLoc.xml" --output="../ValidationFiles/OED_CanLocA.xml" --xml-validation-error-as-warning=true %* "MappingMapToOED_CanLocA.xslt"
IF ERRORLEVEL 1 EXIT/B %ERRORLEVEL%
