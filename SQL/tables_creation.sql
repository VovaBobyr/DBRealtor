CREATE TABLE `byty` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(400) DEFAULT NULL,
  `typ_bytu` varchar(45) DEFAULT NULL,
  `celkova_cena` varchar(200) DEFAULT NULL,
  `poznamka_k_cene` varchar(150) DEFAULT NULL,
  `cena` int(11) DEFAULT NULL,
  `naklady` varchar(45) DEFAULT NULL,
  `id_ext` varchar(45) DEFAULT NULL COMMENT 'ID from external system',
  `aktualizace` varchar(45) DEFAULT NULL,
  `stavba` varchar(45) DEFAULT NULL COMMENT 'state of object',
  `stav_objectu` varchar(45) DEFAULT NULL,
  `vlastnictvi` varchar(45) DEFAULT NULL,
  `podlazi` varchar(150) DEFAULT NULL,
  `uzitna_plocha` varchar(45) DEFAULT NULL,
  `terasa` varchar(45) DEFAULT NULL,
  `sklep` varchar(45) DEFAULT NULL,
  `datum_nastegovani` varchar(45) DEFAULT NULL,
  `rok_kolaudace` varchar(45) DEFAULT NULL,
  `rok_reconstrukce` varchar(45) DEFAULT NULL,
  `voda` varchar(45) DEFAULT NULL,
  `topeni` varchar(45) DEFAULT NULL,
  `odpad` varchar(45) DEFAULT NULL,
  `telekomunikace` varchar(150) DEFAULT NULL,
  `elektrina` varchar(20) DEFAULT NULL,
  `doprava` varchar(100) DEFAULT NULL,
  `komunikace` varchar(45) DEFAULT NULL,
  `energ_narocnost_budovy` varchar(150) DEFAULT NULL,
  `bezbarierovy` varchar(10) DEFAULT NULL,
  `vybaveni` varchar(45) DEFAULT NULL,
  `vytah` varchar(10) DEFAULT NULL,
  `kontakt` varchar(200) DEFAULT NULL,
  `description` varchar(4000) DEFAULT NULL,
  `link` varchar(500) DEFAULT NULL,
  `date_add` datetime DEFAULT NULL,
  `umisteni_objektu` varchar(45) DEFAULT NULL,
  `parkovani` varchar(5) DEFAULT NULL,
  `puvodni_cena` varchar(200) DEFAULT NULL,
  `region` varchar(200) DEFAULT NULL,
  `subregion` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idbyty_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=727 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Table for appartments';
