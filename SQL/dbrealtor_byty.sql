-- MySQL dump 10.13  Distrib 8.0.15, for Win64 (x86_64)
--
-- Host: localhost    Database: dbrealtor
-- ------------------------------------------------------
-- Server version	8.0.15

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
 SET NAMES utf8 ;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `byty`
--

DROP TABLE IF EXISTS `byty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `byty` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(400) DEFAULT NULL,
  `type` varchar(45) DEFAULT NULL,
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
  `energ_narocnost_budovy` varchar(45) DEFAULT NULL,
  `bezbarierovy` varchar(10) DEFAULT NULL,
  `vybaveni` varchar(45) DEFAULT NULL,
  `vytah` varchar(10) DEFAULT NULL,
  `kontakt` varchar(200) DEFAULT NULL,
  `description` varchar(1000) DEFAULT NULL,
  `link` varchar(500) DEFAULT NULL,
  `date_add` date DEFAULT NULL,
  `umisteni_objektu` varchar(45) DEFAULT NULL,
  `parkovani` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idbyty_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Table for appartments';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `byty`
--

LOCK TABLES `byty` WRITE;
/*!40000 ALTER TABLE `byty` DISABLE KEYS */;
INSERT INTO `byty` VALUES (1,NULL,NULL,NULL,NULL,NULL,NULL,'VG504a',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(2,NULL,NULL,NULL,NULL,NULL,NULL,'N05054',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'https://www.sreality.cz/detail/prodej/byt/2+kk/praha-cast-obce-kosire-ulice-plzenska/1409134172#img=0&fullscreen=false','2019-02-28',NULL,NULL),(3,'','','','',NULL,'','','','','','','','','','','','','','','','','','','','','','','','','','','','2019-02-28',NULL,NULL),(4,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2019-02-27',NULL,NULL),(5,'1','','','',0,'','','','','','','','','','','','','','','','','','','','','','','','','','','','2019-02-27',NULL,NULL),(6,'','','','',0,'','','','','','','','','','','','','','','','','','','','','','','','','','','','2019-02-27','',''),(7,'','','','',0,'','','','','','','','','','','','','','','','','','','','','','','','','','','','2019-02-27','','');
/*!40000 ALTER TABLE `byty` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-02-27 19:10:47
