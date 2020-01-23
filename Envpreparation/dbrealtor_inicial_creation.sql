-- --------------------------------------------------------
-- Host:                         178.62.19.21
-- Server version:               5.7.28-0ubuntu0.18.04.4 - (Ubuntu)
-- Server OS:                    Linux
-- HeidiSQL Version:             10.2.0.5599
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- Dumping database structure for dbrealtor
DROP DATABASE IF EXISTS `dbrealtor`;
CREATE DATABASE IF NOT EXISTS `dbrealtor` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `dbrealtor`;

-- Dumping structure for table dbrealtor.byty_prodej
DROP TABLE IF EXISTS `byty_prodej`;
CREATE TABLE IF NOT EXISTS `byty_prodej` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_load` int(11) DEFAULT NULL,
  `title` varchar(400) DEFAULT NULL,
  `typ_bytu` varchar(45) DEFAULT NULL,
  `celkova_cena` varchar(200) DEFAULT NULL,
  `poznamka_k_cene` varchar(150) DEFAULT NULL,
  `cena` int(11) DEFAULT NULL,
  `naklady` varchar(70) DEFAULT NULL,
  `id_ext` varchar(45) DEFAULT NULL COMMENT 'ID from external system',
  `aktualizace` varchar(45) DEFAULT NULL,
  `stavba` varchar(45) DEFAULT NULL COMMENT 'state of object',
  `stav_objektu` varchar(45) DEFAULT NULL,
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
  `date_open` datetime DEFAULT NULL,
  `umisteni_objektu` varchar(45) DEFAULT NULL,
  `parkovani` varchar(5) DEFAULT NULL,
  `puvodni_cena` varchar(200) DEFAULT NULL,
  `region` varchar(200) DEFAULT NULL,
  `subregion` varchar(200) DEFAULT NULL,
  `date_update` datetime DEFAULT NULL,
  `date_close` datetime DEFAULT NULL,
  `status` varchar(1) DEFAULT 'O',
  `obj_number` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idbyty_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=28297 DEFAULT CHARSET=utf8 COMMENT='Table for appartments';

-- Data exporting was unselected.

-- Dumping structure for table dbrealtor.byty_pronajem
DROP TABLE IF EXISTS `byty_pronajem`;
CREATE TABLE IF NOT EXISTS `byty_pronajem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_load` int(11) NOT NULL DEFAULT '0',
  `title` varchar(250) DEFAULT NULL,
  `obj_number` varchar(250) DEFAULT NULL,
  `date_open` datetime DEFAULT NULL,
  `date_update` datetime DEFAULT NULL,
  `status` varchar(1) DEFAULT NULL,
  `date_close` datetime DEFAULT NULL,
  `cena` int(11) DEFAULT NULL,
  `celkova_cena` varchar(100) DEFAULT NULL,
  `poznamka_k_cene` varchar(300) DEFAULT NULL,
  `puvodni_cena` varchar(100) DEFAULT NULL,
  `description` varchar(3000) DEFAULT NULL,
  `link` varchar(300) DEFAULT NULL,
  `region` varchar(100) DEFAULT NULL,
  `subregion` varchar(100) DEFAULT NULL,
  `aktualizace` varchar(25) DEFAULT NULL,
  `id_ext` varchar(25) DEFAULT NULL,
  `stavba` varchar(25) DEFAULT NULL,
  `stav_objektu` varchar(25) DEFAULT NULL,
  `vlastnictvi` varchar(25) DEFAULT NULL,
  `umisteni_objektu` varchar(25) DEFAULT NULL,
  `podlazi` varchar(250) DEFAULT NULL,
  `uzitna_plocha` varchar(25) DEFAULT NULL,
  `terasa` varchar(1) DEFAULT NULL,
  `sklep` varchar(100) DEFAULT NULL,
  `voda` varchar(100) DEFAULT NULL,
  `topeni` varchar(25) DEFAULT NULL,
  `plyn` varchar(25) DEFAULT NULL,
  `odpad` varchar(40) DEFAULT NULL,
  `telekomunikace` varchar(100) DEFAULT NULL,
  `elektrina` varchar(25) DEFAULT NULL,
  `doprava` varchar(100) DEFAULT NULL,
  `komunikace` varchar(25) DEFAULT NULL,
  `vybaveni` varchar(25) DEFAULT NULL,
  `kontakt` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17814 DEFAULT CHARSET=utf8 COMMENT='Save all from pronajem SReality';

-- Data exporting was unselected.

-- Dumping structure for table dbrealtor.dataloadlog
DROP TABLE IF EXISTS `dataloadlog`;
CREATE TABLE IF NOT EXISTS `dataloadlog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(50) DEFAULT NULL,
  `date_start` datetime DEFAULT NULL,
  `date_finish` datetime DEFAULT NULL,
  `status` varchar(10) DEFAULT NULL,
  `items_count` int(11) DEFAULT NULL,
  `pages_count` int(11) DEFAULT NULL,
  `inserted_count` int(11) DEFAULT NULL,
  `skipped_count` int(11) DEFAULT NULL,
  `failed_count` int(11) DEFAULT NULL,
  `closed_count` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=198 DEFAULT CHARSET=latin1 COMMENT='Save dataloading';

-- Data exporting was unselected.

-- Dumping structure for table dbrealtor.domy_prodej
DROP TABLE IF EXISTS `domy_prodej`;
CREATE TABLE IF NOT EXISTS `domy_prodej` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_load` int(11) DEFAULT NULL,
  `link` varchar(500) CHARACTER SET utf8 DEFAULT NULL,
  `date_open` datetime DEFAULT NULL,
  `date_update` datetime DEFAULT NULL,
  `date_close` datetime DEFAULT NULL,
  `status` varchar(1) CHARACTER SET utf8 DEFAULT 'O',
  `obj_number` varchar(15) CHARACTER SET utf8 DEFAULT NULL,
  `region` varchar(200) CHARACTER SET utf8 DEFAULT NULL,
  `subregion` varchar(200) CHARACTER SET utf8 DEFAULT NULL,
  `title` varchar(400) CHARACTER SET utf8 DEFAULT NULL,
  `description` varchar(4000) CHARACTER SET utf8 DEFAULT NULL,
  `puvodni_cena` varchar(200) CHARACTER SET utf8 DEFAULT NULL,
  `celkova_cena` varchar(200) CHARACTER SET utf8 DEFAULT NULL,
  `poznamka_k_cene` varchar(150) CHARACTER SET utf8 DEFAULT NULL,
  `cena` int(11) DEFAULT NULL,
  `naklady` varchar(300) CHARACTER SET utf8 DEFAULT NULL,
  `id_ext` varchar(55) CHARACTER SET utf8 DEFAULT NULL COMMENT 'ID zakazky',
  `aktualizace` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `stavba` varchar(45) CHARACTER SET utf8 DEFAULT NULL COMMENT 'state of object',
  `stav_objektu` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `umisteni_objektu:` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `typ_domu` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `vlastnictvi` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `podlazi` varchar(150) CHARACTER SET utf8 DEFAULT NULL,
  `pocet_bytu` varchar(10) CHARACTER SET utf8 DEFAULT NULL,
  `plocha_domu` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `plocha_zastavena` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `uzitna_plocha` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `plocha_podlahova` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `plocha_pozemku` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `plocha_zahrady` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `parkovani` varchar(10) CHARACTER SET utf8 DEFAULT NULL,
  `garaz` varchar(10) CHARACTER SET utf8 DEFAULT NULL,
  `terasa` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `sklep` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `datum_nastegovani` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `rok_kolaudace` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `rok_reconstrukce` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `voda` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `topeni` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `plyn` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `odpad` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `telekomunikace` varchar(150) CHARACTER SET utf8 DEFAULT NULL,
  `elektrina` varchar(20) CHARACTER SET utf8 DEFAULT NULL,
  `doprava` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `komunikace` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `energ_narocnost_budovy` varchar(150) CHARACTER SET utf8 DEFAULT NULL,
  `bezbarierovy` varchar(10) CHARACTER SET utf8 DEFAULT NULL,
  `vybaveni` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `bazen` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `umisteni_objektu` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `kontakt` varchar(200) CHARACTER SET utf8 DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idbyty_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21731 DEFAULT CHARSET=latin1 COMMENT='Table for prodej domu';

-- Data exporting was unselected.

-- Dumping structure for table dbrealtor.domy_pronajem
DROP TABLE IF EXISTS `domy_pronajem`;
CREATE TABLE IF NOT EXISTS `domy_pronajem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_load` int(11) NOT NULL DEFAULT '0',
  `title` varchar(400) DEFAULT NULL,
  `obj_number` varchar(250) DEFAULT NULL,
  `date_open` datetime DEFAULT NULL,
  `date_update` datetime DEFAULT NULL,
  `date_close` datetime DEFAULT NULL,
  `status` varchar(1) DEFAULT NULL,
  `cena` int(11) DEFAULT NULL,
  `celkova_cena` varchar(100) DEFAULT NULL,
  `poznamka_k_cene` varchar(300) DEFAULT NULL,
  `puvodni_cena` varchar(100) DEFAULT NULL,
  `description` varchar(3000) DEFAULT NULL,
  `link` varchar(300) DEFAULT NULL,
  `region` varchar(100) DEFAULT NULL,
  `subregion` varchar(100) DEFAULT NULL,
  `aktualizace` varchar(25) DEFAULT NULL,
  `id_ext` varchar(25) DEFAULT NULL,
  `stavba` varchar(25) DEFAULT NULL,
  `naklady` varchar(100) DEFAULT NULL,
  `stav_objektu` varchar(25) DEFAULT NULL,
  `vlastnictvi` varchar(25) DEFAULT NULL,
  `pocet_bytu` varchar(25) DEFAULT NULL,
  `umisteni_objektu` varchar(25) DEFAULT NULL,
  `podlazi` varchar(50) DEFAULT NULL,
  `uzitna_plocha` varchar(25) DEFAULT NULL,
  `plocha_domu` varchar(25) DEFAULT NULL,
  `plocha_zastavena` varchar(25) DEFAULT NULL,
  `typ_domu` varchar(25) DEFAULT NULL,
  `plocha_pozemku` varchar(25) DEFAULT NULL,
  `plocha_zahrady` varchar(25) DEFAULT NULL,
  `plocha_podlahova` varchar(25) DEFAULT NULL,
  `rok_rekonstrukce` varchar(10) DEFAULT NULL,
  `rok_kolaudace` varchar(25) DEFAULT NULL,
  `terasa` varchar(1) DEFAULT NULL,
  `sklep` varchar(100) DEFAULT NULL,
  `voda` varchar(100) DEFAULT NULL,
  `topeni` varchar(25) DEFAULT NULL,
  `plyn` varchar(25) DEFAULT NULL,
  `odpad` varchar(40) DEFAULT NULL,
  `telekomunikace` varchar(100) DEFAULT NULL,
  `datum_nastegovani` varchar(45) DEFAULT NULL,
  `energ_narocnost_budovy` varchar(300) DEFAULT NULL,
  `elektrina` varchar(25) DEFAULT NULL,
  `rok_reconstrukce` varchar(25) DEFAULT NULL,
  `doprava` varchar(100) DEFAULT NULL,
  `komunikace` varchar(25) DEFAULT NULL,
  `parkovani` varchar(25) DEFAULT NULL,
  `vybaveni` varchar(1) DEFAULT NULL,
  `garaz` varchar(1) DEFAULT NULL,
  `bezbarierovy` varchar(1) DEFAULT NULL,
  `bazen` varchar(1) DEFAULT NULL,
  `kontakt` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=945 DEFAULT CHARSET=utf8 COMMENT='Save all from pronajem SReality';

-- Data exporting was unselected.

-- Dumping structure for table dbrealtor.projekty
DROP TABLE IF EXISTS `projekty`;
CREATE TABLE IF NOT EXISTS `projekty` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_load` int(11) NOT NULL,
  `obj_number` varchar(45) NOT NULL COMMENT 'Number from external',
  `link` varchar(200) NOT NULL,
  `title` varchar(200) DEFAULT NULL,
  `region` varchar(200) DEFAULT NULL,
  `subregion` varchar(70) DEFAULT NULL,
  `date_open` datetime DEFAULT NULL,
  `date_update` datetime DEFAULT NULL,
  `date_close` datetime DEFAULT NULL,
  `status` varchar(8) DEFAULT 'open',
  `zahajeni_prodeje` varchar(15) DEFAULT NULL,
  `dokonceni_vystavby` varchar(15) DEFAULT NULL,
  `k_nastehovani` varchar(15) DEFAULT NULL,
  `description` varchar(3000) DEFAULT NULL,
  `vnitrni_omitky` varchar(50) DEFAULT NULL,
  `zaklady` varchar(200) DEFAULT NULL,
  `vnitrni_obklady` varchar(50) DEFAULT NULL,
  `fasadni_omitky` varchar(50) DEFAULT NULL,
  `stropy` varchar(100) DEFAULT NULL,
  `podlahy` varchar(100) DEFAULT NULL,
  `okna` varchar(100) DEFAULT NULL,
  `dvere` varchar(100) DEFAULT NULL,
  `kuchynska_linka` varchar(100) DEFAULT NULL,
  `zastavba` varchar(100) DEFAULT NULL,
  `zelezobetonove_schodiste` varchar(50) DEFAULT NULL,
  `interierove_schodiste` varchar(100) DEFAULT NULL,
  `stav_objektu` varchar(100) DEFAULT NULL,
  `krytina` varchar(100) DEFAULT NULL,
  `umisteni_objektu` varchar(100) DEFAULT NULL,
  `strecha` varchar(100) DEFAULT NULL,
  `komunikace` varchar(100) DEFAULT NULL,
  `vnejsi_obklady` varchar(100) DEFAULT NULL,
  `prevod_do_ov` varchar(10) DEFAULT NULL,
  `stavba` varchar(50) DEFAULT NULL,
  `vlastnictvi` varchar(50) DEFAULT NULL,
  `typ_domu` varchar(50) DEFAULT NULL,
  `poloha_domu` varchar(50) DEFAULT NULL,
  `kontakt` varchar(1000) DEFAULT NULL,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=471 DEFAULT CHARSET=utf8 COMMENT='Table for save common details for project\r\nIt refers to details about specific items (byt,dom) - table projekt_items';

-- Data exporting was unselected.

-- Dumping structure for table dbrealtor.projekty_items
DROP TABLE IF EXISTS `projekty_items`;
CREATE TABLE IF NOT EXISTS `projekty_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_load` int(11) DEFAULT NULL,
  `proj_number` varchar(45) DEFAULT NULL COMMENT 'Linkt to projekt table - obj_number',
  `title` varchar(400) DEFAULT NULL,
  `type_item` varchar(45) DEFAULT NULL,
  `celkova_cena` varchar(200) DEFAULT NULL,
  `poznamka_k_cene` varchar(150) DEFAULT NULL,
  `cena` int(11) DEFAULT NULL,
  `puvodni_cena` varchar(200) DEFAULT NULL,
  `region` varchar(200) DEFAULT NULL,
  `subregion` varchar(200) DEFAULT NULL,
  `date_open` datetime DEFAULT NULL,
  `date_update` datetime DEFAULT NULL,
  `date_close` datetime DEFAULT NULL,
  `status` varchar(1) DEFAULT 'O',
  `obj_number` varchar(15) DEFAULT NULL,
  `naklady` varchar(70) DEFAULT NULL,
  `id_ext` varchar(45) DEFAULT NULL COMMENT 'ID from external system',
  `aktualizace` varchar(45) DEFAULT NULL,
  `stavba` varchar(45) DEFAULT NULL COMMENT 'state of object',
  `stav_objektu` varchar(45) DEFAULT NULL,
  `vlastnictvi` varchar(45) DEFAULT NULL,
  `podlazi` varchar(150) DEFAULT NULL,
  `uzitna_plocha` varchar(45) DEFAULT NULL,
  `terasa` varchar(45) DEFAULT NULL,
  `typ_domu` varchar(70) DEFAULT NULL,
  `sklep` varchar(45) DEFAULT NULL,
  `pocet_bytu` varchar(45) DEFAULT NULL,
  `datum_nastegovani` varchar(45) DEFAULT NULL,
  `rok_kolaudace` varchar(45) DEFAULT NULL,
  `rok_reconstrukce` varchar(45) DEFAULT NULL,
  `voda` varchar(45) DEFAULT NULL,
  `topeni` varchar(45) DEFAULT NULL,
  `plyn` varchar(45) DEFAULT NULL,
  `odpad` varchar(45) DEFAULT NULL,
  `telekomunikace` varchar(150) DEFAULT NULL,
  `elektrina` varchar(20) DEFAULT NULL,
  `doprava` varchar(100) DEFAULT NULL,
  `komunikace` varchar(45) DEFAULT NULL,
  `energ_narocnost_budovy` varchar(150) DEFAULT NULL,
  `bezbarierovy` varchar(10) DEFAULT NULL,
  `vybaveni` varchar(45) DEFAULT NULL,
  `vytah` varchar(10) DEFAULT NULL,
  `bazen` varchar(10) DEFAULT NULL,
  `garaz` varchar(45) DEFAULT NULL,
  `kontakt` varchar(200) DEFAULT NULL,
  `description` varchar(4000) DEFAULT NULL,
  `link` varchar(500) DEFAULT NULL,
  `umisteni_objektu` varchar(45) DEFAULT NULL,
  `parkovani` varchar(5) DEFAULT NULL,
  `plocha_domu` varchar(30) DEFAULT NULL,
  `plocha_podlahova` varchar(30) DEFAULT NULL,
  `plocha_zastavena` varchar(30) DEFAULT NULL,
  `plocha_pozemku` varchar(30) DEFAULT NULL,
  `plocha_zahrady` varchar(30) DEFAULT NULL,
  `datum_ukonceni_vystavby` varchar(30) DEFAULT NULL,
  `datum_zahajeni_prodeje` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idbyty_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1494 DEFAULT CHARSET=utf8 COMMENT='Table for appartments';

-- Data exporting was unselected.

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
