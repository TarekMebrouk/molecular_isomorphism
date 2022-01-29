-- phpMyAdmin SQL Dump
-- version 4.8.4
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le :  sam. 29 jan. 2022 à 11:38
-- Version du serveur :  5.7.24
-- Version de PHP :  7.2.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données :  `molecular_isomorphism`
--

-- --------------------------------------------------------

--
-- Structure de la table `lab`
--

DROP TABLE IF EXISTS `lab`;
CREATE TABLE IF NOT EXISTS `lab` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_chebi` varchar(50) NOT NULL,
  `atom_id` int(11) NOT NULL,
  `index` int(11) NOT NULL,
  `ctype` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `SECONDARY_KEY_2` (`id_chebi`)
) ENGINE=InnoDB AUTO_INCREMENT=10063 DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `links`
--

DROP TABLE IF EXISTS `links`;
CREATE TABLE IF NOT EXISTS `links` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_chebi` varchar(100) NOT NULL,
  `atom_from` int(11) NOT NULL,
  `atom_to` int(11) NOT NULL,
  `version` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `SECONDARY_KEY_1` (`id_chebi`)
) ENGINE=InnoDB AUTO_INCREMENT=19121 DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `molecules`
--

DROP TABLE IF EXISTS `molecules`;
CREATE TABLE IF NOT EXISTS `molecules` (
  `id_chebi` varchar(50) NOT NULL,
  `name` text NOT NULL,
  `formula` text NOT NULL,
  `dimension` varchar(10) NOT NULL,
  `family` text NOT NULL,
  `maximum_link` int(11) NOT NULL,
  `atoms_number` int(11) NOT NULL,
  `links_number` int(11) NOT NULL,
  `atoms` text NOT NULL,
  `positions` text NOT NULL,
  `links` text NOT NULL,
  `colored_atoms_number` int(11) DEFAULT NULL,
  `colored_links_number` int(11) DEFAULT NULL,
  `atoms_colored` text,
  `links_colored` text,
  `canonical_form1` text,
  `canonical_form2` text,
  `canonical_form3` text,
  `canonical_label1` text,
  `canonical_label2` text,
  `canonical_label3` text,
  `time` double DEFAULT NULL,
  PRIMARY KEY (`id_chebi`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `ptn`
--

DROP TABLE IF EXISTS `ptn`;
CREATE TABLE IF NOT EXISTS `ptn` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_chebi` varchar(50) NOT NULL,
  `ptn` text NOT NULL,
  `version` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `SECONDARY_KEY_3` (`id_chebi`)
) ENGINE=InnoDB AUTO_INCREMENT=657 DEFAULT CHARSET=utf8;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `lab`
--
ALTER TABLE `lab`
  ADD CONSTRAINT `SECONDARY_KEY_2` FOREIGN KEY (`id_chebi`) REFERENCES `molecules` (`id_chebi`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `links`
--
ALTER TABLE `links`
  ADD CONSTRAINT `SECONDARY_KEY_1` FOREIGN KEY (`id_chebi`) REFERENCES `molecules` (`id_chebi`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `ptn`
--
ALTER TABLE `ptn`
  ADD CONSTRAINT `SECONDARY_KEY_3` FOREIGN KEY (`id_chebi`) REFERENCES `molecules` (`id_chebi`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
