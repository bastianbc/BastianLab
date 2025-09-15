
"""
CREATE MATERIALIZED VIEW variants_view AS
SELECT DISTINCT ON (vc.id)
    ROW_NUMBER() OVER() AS id,
    vc.id AS variantcall_id,
    a.id AS area_id,
    a.name AS area_name,
    a.area_type,
    a.collection,
    b.id AS block_id,
    b.name AS block_name,
    sl.id AS samplelib_id,
    sl.name AS samplelib_name,
    g.id AS gene_id,
    g.name AS gene_name,
    g.chr AS chromosome,
    vc.coverage,
    vc.log2r,
    vc.caller,
    vc.ref_read,
    vc.alt_read,
    CASE
        WHEN vc.ref_read > 0 THEN (vc.alt_read * 100.0) / (vc.ref_read + vc.alt_read)
        ELSE 0.0
    END AS vaf,
    vc.alias_meta as "alias",
    vc.variant_meta as "variant",
    gv.id AS gvariant_id,
    gv.chrom AS g_chromosome,
    gv.start AS g_start,
    gv.end AS g_end,
    gv.ref AS g_ref,
    gv.alt AS g_alt,
    gv.avsnp150,
    cv.id AS cvariant_id,
    cv.nm_id,
    cv.c_var,
    cv.exon,
    cv.func,
    pv.id AS pvariant_id,
    pv.reference_residues,
    pv.inserted_residues,
    pv.change_type,
    ar.id AS analysis_run_id,
    ar.name AS analysis_run_name,
    cgv.gene_symbol AS cosmic_gene_symbol,
    cgv.cosmic_aa,
    cgv.primary_site_counts AS cosmic_primary_site_counts,
    (
        SELECT COALESCE(SUM((value)::int), 0)
        FROM jsonb_each_text(cgv.primary_site_counts)
    ) AS total_site_counts
FROM
    areas a
JOIN
    block b ON a.block = b.id
JOIN
    area_na_link anl ON anl.area_id = a.id
JOIN
    nuc_acids na ON anl.nucacid_id = na.id
JOIN
    na_sl_link nsl ON nsl.nucacid_id = na.id
JOIN
    sample_lib sl ON nsl.sample_lib_id = sl.id
JOIN
    variant_call vc ON vc.sample_lib_id = sl.id
JOIN
    g_variant gv ON gv.id = vc.g_variant_id
JOIN
    c_variant cv ON cv.g_variant_id = gv.id
JOIN
    gene g ON cv.gene_id = g.id
JOIN
    analysis_run ar ON vc.analysis_run_id = ar.id
LEFT JOIN
    p_variant pv ON pv.c_variant_id = cv.id
LEFT JOIN
    cosmic_hg38.cosmic_g_variant_view_with_id_stats cgv on cgv.g_variant_id=gv.id
WHERE
    a.area_type IS NOT NULL;
"""


'''
CREATE MATERIALIZED VIEW variants_view_consolidated AS
SELECT DISTINCT ON (vc.variantcall_id)
    ROW_NUMBER() OVER() AS id,
    vc.variantcall_id AS variantcall_id,
    a.id AS area_id,
    a.name AS area_name,
    a.area_type,
    a.collection,
    b.id AS block_id,
    b.name AS block_name,
    sl.id AS samplelib_id,
    sl.name AS samplelib_name,
    g.id AS gene_id,
    g.name AS gene_name,
    g.chr AS chromosome,
    vc.coverage,
    vc.log2r,
    vc.callers_fmh as caller,
    vc.ref_read,
    vc.alt_read,
    CASE
        WHEN vc.ref_read > 0 THEN (vc.alt_read * 100.0) / (vc.ref_read + vc.alt_read)
        ELSE 0.0
    END AS vaf,
    vc.alias_meta as "alias",
    vc.variant_meta as "variant",
    gv.id AS gvariant_id,
    gv.chrom AS g_chromosome,
    gv.start AS g_start,
    gv.end AS g_end,
    gv.ref AS g_ref,
    gv.alt AS g_alt,
    gv.avsnp150,
    cv.id AS cvariant_id,
    cv.nm_id,
    cv.c_var,
    cv.exon,
    cv.func,
    pv.id AS pvariant_id,
    pv.reference_residues,
    pv.inserted_residues,
    pv.change_type,
    ar.id AS analysis_run_id,
    ar.name AS analysis_run_name,
    cgv.gene_symbol AS cosmic_gene_symbol,
    cgv.cosmic_aa,
    cgv.primary_site_counts AS cosmic_primary_site_counts,
    (
        SELECT COALESCE(SUM((value)::int), 0)
        FROM jsonb_each_text(cgv.primary_site_counts)
    ) AS total_site_counts
FROM
    areas a
JOIN
    block b ON a.block = b.id
JOIN
    area_na_link anl ON anl.area_id = a.id
JOIN
    nuc_acids na ON anl.nucacid_id = na.id
JOIN
    na_sl_link nsl ON nsl.nucacid_id = na.id
JOIN
    sample_lib sl ON nsl.sample_lib_id = sl.id
JOIN
    variant_call_preferred vc ON vc.sample_lib_id = sl.id
JOIN
    g_variant gv ON gv.id = vc.g_variant_id
JOIN
    c_variant cv ON cv.g_variant_id = gv.id
JOIN
    gene g ON cv.gene_id = g.id
JOIN
    analysis_run ar ON vc.analysis_run_id = ar.id
LEFT JOIN
    p_variant pv ON pv.c_variant_id = cv.id
LEFT JOIN
    cosmic_hg38.cosmic_g_variant_view_with_id_stats cgv on cgv.g_variant_id=gv.id
WHERE
    a.area_type IS NOT NULL;
'''

# Here are some database indexes after need to create after to created the materialized view above
"""
CREATE UNIQUE INDEX ON variants_view (id);
CREATE INDEX idx_area_variants_area_id ON variants_view (area_id);
CREATE INDEX idx_area_variants_block_id ON variants_view (block_id);
"""

# Here are some helpfull commands
"""
drop materialized view variants_view;

select * from pg_catalog.pg_matviews;
"""


# Variants Count view
"""
CREATE MATERIALIZED VIEW variant_counts AS
SELECT
    b.id   AS block_id,
    b.name AS block_name,
    a.id   AS area_id,
    a.name AS area_name,

    -- count variants linked via this area only
    COUNT(DISTINCT gv.id) AS areas_variant_count,

    -- count variants linked via ALL areas under the same block
    (
        SELECT COUNT(DISTINCT gv2.id)
        FROM areas a2
        JOIN area_na_link anl2
          ON anl2.area_id = a2.id
        JOIN nuc_acids na2
          ON na2.id = anl2.nucacid_id
        JOIN na_sl_link nsl2
          ON nsl2.nucacid_id = na2.id
        JOIN sample_lib sl2
          ON sl2.id = nsl2.sample_lib_id
        JOIN variant_call vc2
          ON vc2.sample_lib_id = sl2.id
        JOIN g_variant gv2
          ON gv2.id = vc2.g_variant_id
        WHERE a2.block = b.id
    ) AS block_variant_count

FROM block b
JOIN areas a
  ON b.id = a.block
LEFT JOIN area_na_link anl
  ON anl.area_id = a.id
LEFT JOIN nuc_acids na
  ON na.id = anl.nucacid_id
LEFT JOIN na_sl_link nsl
  ON nsl.nucacid_id = na.id
LEFT JOIN sample_lib sl
  ON sl.id = nsl.sample_lib_id
LEFT JOIN variant_call vc
  ON vc.sample_lib_id = sl.id
LEFT JOIN g_variant gv
  ON gv.id = vc.g_variant_id

GROUP BY a.id, a.name, b.id, b.name
ORDER BY block_variant_count DESC, areas_variant_count DESC;
"""