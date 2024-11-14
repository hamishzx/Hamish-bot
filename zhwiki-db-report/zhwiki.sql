SELECT wpg.page_title
FROM zhwiki_p.page wpg
LEFT JOIN zhwiki_p.image wpimg
ON wpimg.img_name = wpg.page_title
WHERE wpg.page_namespace=6 AND wpimg.img_name IS null;