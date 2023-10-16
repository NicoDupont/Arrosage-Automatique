-- phpMyAdmin SQL Dump
-- version 4.9.7
-- https://www.phpmyadmin.net/
--
-- Hôte : localhost
-- Généré le : lun. 16 oct. 2023 à 22:18
-- Version du serveur :  10.3.29-MariaDB
-- Version de PHP : 7.4.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `ARROSAGE`
--

-- --------------------------------------------------------

--
-- Structure de la table `Event`
--

CREATE TABLE `Event` (
  `id_event` int(11) NOT NULL,
  `eventdate` datetime NOT NULL DEFAULT current_timestamp(),
  `val1` varchar(100) DEFAULT NULL,
  `val2` varchar(100) DEFAULT NULL,
  `val3` varchar(100) DEFAULT NULL,
  `val4` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `mesure`
--

CREATE TABLE `mesure` (
  `id` int(11) NOT NULL,
  `mesure_ts` timestamp NOT NULL DEFAULT current_timestamp(),
  `mesure` float NOT NULL,
  `id_sensor` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `mesure_last`
--

CREATE TABLE `mesure_last` (
  `id` int(11) NOT NULL,
  `id_sensor` int(11) NOT NULL,
  `mesure` float NOT NULL,
  `mesure_tm` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `Parameter`
--

CREATE TABLE `Parameter` (
  `id_parameter` int(11) NOT NULL,
  `mode` varchar(20) NOT NULL DEFAULT 'Auto',
  `source` varchar(100) DEFAULT NULL,
  `test` int(11) NOT NULL,
  `duree_test` int(11) NOT NULL,
  `gestion_cuve` int(11) NOT NULL DEFAULT 1,
  `heure_debut_sequence` int(11) NOT NULL,
  `heure_debut_sequence_demande` int(11) NOT NULL DEFAULT 0,
  `minute_debut_sequence` int(11) NOT NULL DEFAULT 0,
  `minute_debut_sequence_demande` int(11) NOT NULL DEFAULT 0,
  `duree_coef` int(11) NOT NULL,
  `pression_seuil_bas` float NOT NULL,
  `pression_seuil_haut` float DEFAULT NULL,
  `pression_canal_amont` float NOT NULL,
  `pression_canal_aval` float NOT NULL,
  `pression_cuve_amont` float NOT NULL,
  `pression_cuve_aval` float NOT NULL,
  `pression_ville` float NOT NULL,
  `pression_arrosage` float NOT NULL,
  `debitmetre_cuve` float NOT NULL,
  `debimetre_arrosage` float NOT NULL,
  `test_pression_cuve` int(11) NOT NULL,
  `test_pression_canal` int(11) NOT NULL,
  `test_pression_ville` int(11) NOT NULL,
  `hauteur_eau_cuve` int(11) NOT NULL,
  `test_hauteur_eau_cuve` int(11) NOT NULL,
  `delta_pression_filtre_max` float NOT NULL,
  `nb_cuve_ibc` int(11) NOT NULL,
  `nb_litre_cuve_ibc` int(11) NOT NULL,
  `seuil_min_capacite_cuve` int(11) NOT NULL,
  `seuil_max_capacite_cuve` int(11) NOT NULL,
  `seuil_capacite_remplissage_auto_cuve` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `sensor`
--

CREATE TABLE `sensor` (
  `id` int(11) NOT NULL,
  `sensor` mediumtext NOT NULL,
  `description` mediumtext NOT NULL,
  `type` varchar(40) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `SequenceZone`
--

CREATE TABLE `SequenceZone` (
  `id_sequence` int(11) NOT NULL,
  `id_sv` int(11) DEFAULT NULL,
  `sv` varchar(10) DEFAULT NULL,
  `name` varchar(150) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `open` int(11) DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `StartingDate` timestamp NULL DEFAULT NULL,
  `EndDate` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `Zone`
--

CREATE TABLE `Zone` (
  `id_sv` int(11) NOT NULL,
  `type` varchar(10) NOT NULL DEFAULT 'zone',
  `systeme` varchar(30) NOT NULL DEFAULT 'Tuyere',
  `sv` varchar(10) NOT NULL,
  `order` int(11) NOT NULL,
  `gpio` int(11) NOT NULL,
  `name` varchar(150) NOT NULL,
  `open` int(11) NOT NULL,
  `active` int(11) NOT NULL,
  `sequence` int(11) NOT NULL,
  `duration` int(11) NOT NULL,
  `test` int(11) NOT NULL DEFAULT 0,
  `even` int(11) NOT NULL,
  `odd` int(11) NOT NULL DEFAULT 0,
  `monday` int(11) NOT NULL,
  `tuesday` int(11) NOT NULL,
  `wednesday` int(11) NOT NULL,
  `thursday` int(11) NOT NULL,
  `friday` int(11) NOT NULL,
  `saturday` int(11) NOT NULL,
  `sunday` int(11) NOT NULL,
  `coef` int(11) NOT NULL,
  `rpi` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `Event`
--
ALTER TABLE `Event`
  ADD PRIMARY KEY (`id_event`);

--
-- Index pour la table `mesure`
--
ALTER TABLE `mesure`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `mesure_last`
--
ALTER TABLE `mesure_last`
  ADD KEY `id` (`id`);

--
-- Index pour la table `Parameter`
--
ALTER TABLE `Parameter`
  ADD PRIMARY KEY (`id_parameter`);

--
-- Index pour la table `sensor`
--
ALTER TABLE `sensor`
  ADD UNIQUE KEY `id` (`id`);

--
-- Index pour la table `SequenceZone`
--
ALTER TABLE `SequenceZone`
  ADD KEY `ix_Sequence` (`id_sequence`) USING BTREE;

--
-- Index pour la table `Zone`
--
ALTER TABLE `Zone`
  ADD PRIMARY KEY (`id_sv`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `Event`
--
ALTER TABLE `Event`
  MODIFY `id_event` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `mesure`
--
ALTER TABLE `mesure`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `mesure_last`
--
ALTER TABLE `mesure_last`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `Parameter`
--
ALTER TABLE `Parameter`
  MODIFY `id_parameter` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `sensor`
--
ALTER TABLE `sensor`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `SequenceZone`
--
ALTER TABLE `SequenceZone`
  MODIFY `id_sequence` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `Zone`
--
ALTER TABLE `Zone`
  MODIFY `id_sv` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
