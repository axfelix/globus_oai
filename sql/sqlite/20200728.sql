UPDATE repositories SET repo_oai_name = REPLACE(REPLACE(SUBSTR(homepage_url,9),'/','-'),'www.','') where homepage_url like 'https%' and repo_oai_name = '';
UPDATE repositories SET repo_oai_name = REPLACE(REPLACE(SUBSTR(homepage_url,8),'/','-'),'www.','') where homepage_url like 'http%' and repo_oai_name = '';
UPDATE repositories SET repo_oai_name = SUBSTR(repo_oai_name,1,LENGTH(repo_oai_name)-1) where repo_oai_name like '%-';