param(
  [string]$Root = "."
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RootPath = (Resolve-Path $Root).Path
$Required = @(
  "main.tex",
  "sections/introduction.tex",
  "sections/modelling_methods.tex",
  "sections/mosaicity_texture.tex",
  "sections/refinement_workflow.tex",
  "sections/results_ordered.tex",
  "sections/results_diffuse_pbi2.tex",
  "2D_Supplemental/SI_failure_modes.tex"
)

foreach ($Rel in $Required) {
  $Path = Join-Path $RootPath $Rel
  if (-not (Test-Path $Path)) {
    throw "Missing required file: $Rel. Run this script from the manuscript root or pass -Root <path>."
  }
}

$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$script:BackedUp = @{}
$Utf8NoBom = [System.Text.UTF8Encoding]::new($false)

function Backup-File {
  param([string]$RelPath)
  if ($script:BackedUp.ContainsKey($RelPath)) { return }
  $Path = Join-Path $RootPath $RelPath
  Copy-Item -LiteralPath $Path -Destination "$Path.bak-$Timestamp"
  $script:BackedUp[$RelPath] = $true
}

function Write-TextFile {
  param([string]$RelPath, [string]$Content)
  Backup-File $RelPath
  $Path = Join-Path $RootPath $RelPath
  [System.IO.File]::WriteAllText($Path, ($Content.TrimEnd() + "`n"), $Utf8NoBom)
}

function Read-Normalized {
  param([string]$RelPath)
  $Path = Join-Path $RootPath $RelPath
  return ([System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8) -replace "`r`n", "`n")
}

function Update-TextFile {
  param([string]$RelPath, [scriptblock]$Updater)
  Backup-File $RelPath
  $Path = Join-Path $RootPath $RelPath
  $Text = Read-Normalized $RelPath
  $NewText = & $Updater $Text
  [System.IO.File]::WriteAllText($Path, ($NewText.TrimEnd() + "`n"), $Utf8NoBom)
}

function Replace-OnceRegex {
  param([string]$Text, [string]$Pattern, [string]$Replacement, [string]$Description)
  $Options = [System.Text.RegularExpressions.RegexOptions]::Singleline
  $Rx = [System.Text.RegularExpressions.Regex]::new($Pattern, $Options)
  if (-not $Rx.IsMatch($Text)) { throw "Could not find block for: $Description" }
  $script:DidReplace = $false
  return $Rx.Replace($Text, [System.Text.RegularExpressions.MatchEvaluator]{
    param($Match)
    if ($script:DidReplace) { return $Match.Value }
    $script:DidReplace = $true
    return $Replacement
  })
}

function Replace-BetweenLiterals {
  param([string]$Text, [string]$StartLiteral, [string]$EndLiteral, [string]$Replacement, [string]$Description)
  $Start = $Text.IndexOf($StartLiteral)
  if ($Start -lt 0) { throw "Could not find start marker for: $Description" }
  $End = $Text.IndexOf($EndLiteral, $Start + $StartLiteral.Length)
  if ($End -lt 0) { throw "Could not find end marker for: $Description" }
  return $Text.Substring(0, $Start) + $Replacement.TrimEnd() + "`n" + $Text.Substring($End)
}

# 1. Fix the introduction claim that the manuscript refines every image pixel by pixel.
$NewIntroParagraph = @'
Here we present a quantitative forward model for WAXS from two-dimensional powders that predicts full area-detector images and then refines stage-specific detector-derived observables against measured data. Prior work has established the main ingredients needed for such a framework, including grazing-incidence scattering formalisms,\cite{Sinha1988,Renaud2009} reciprocal-space mapping and indexing for oriented thin films,\cite{SmilgiesBlasini2007,Smilgies2005Rods,Hexemer2015,Savikhin2020} and forward simulation of diffraction from textured films.\cite{Breiby2008} Complementary atomistic tools have also been developed for constructing commensurate multilayer 2D heterostructure supercells and visualizing their reciprocal-space diffraction signatures, including Nookiin.\cite{AguilarSpindola2026Nookiin} In contrast, the present work takes the crystallographic model as input and carries the calculation in detector space through the coupled effects of detector geometry, grazing-incidence propagation, mosaicity, and stacking disorder. Geometry is constrained by detector-space peak positions, mosaicity by local profile shapes, ordered structure by selected Bragg-ROI intensities, and disorder by selected-rod profiles. Our contribution is to combine these ingredients in a single self-consistent refinement scheme tailored to 2D powders. We validate the ordered 2D-powder limit using Bi$_2$Se$_3$ and Bi$_2$Te$_3$ films,\cite{Jerng2013,Zhang2022Bi2Te3} and we then apply the same framework to disordered PbI$_2$ to extract effective stacking-disorder parameters from diffuse $Q_z$ intensity in selected $Q_r/Q_z$ rod profiles that are typically masked in 1D-integrated analyses (see supporting information, Fig.~S1, Sec.~S1.3, and Secs.~S2--S3).\cite{Treacy1991,CasasCabanas2016} By embedding geometric and sample effects within a single forward model, we avoid separating geometric corrections from structural fitting and instead refine geometry, mosaicity, ordered intensity, and disorder within a common detector-space framework.
'@

Update-TextFile "sections/introduction.tex" {
  param($Text)
  Replace-OnceRegex $Text "Here we present a quantitative forward model for WAXS from two-dimensional powders.*?(?=\n\s*\\pagebreak)" $NewIntroParagraph "introduction detector-space objective paragraph"
}

# 2. Clarify that pixel-level detector images are predicted by the forward model, not used as one global objective everywhere.
$NewMethodsIntro = @'
We model the measured area-detector intensity by building the diffraction process in the same order used throughout this section. We first determine the allowed exit vectors $\mathbf{k}_f$ for the simplest elastic-scattering geometry, then extend that construction to the finite beam, sample, and detector geometry of the experiment. For each allowed reciprocal-space intersection, the crystallographic model supplies the structure-factor weight, and the mosaicity model redistributes that weight over the nearby \(\mathbf{k}_f\) values appropriate to a two-dimensional powder. The result is a full detector-space image calculation with intensity deposited on detector pixels. That image is the common forward object for the workflow, but the refinement objectives are stage-specific: peak centers for geometry, local Gaussian-plus-Lorentzian line shapes for mosaicity, detector-space Bragg ROI integrals for ordered intensity, and selected-rod profiles for disorder.
'@

Update-TextFile "sections/modelling_methods.tex" {
  param($Text)
  Replace-OnceRegex $Text "We model the measured area-detector intensity.*?(?=\n\s*\\subsection\{Diffraction Geometry\})" $NewMethodsIntro "modelling-methods forward-object paragraph"
}

# 3. Replace the mosaicity subsection. This removes the unwrapped main-text formula and avoids pseudo-Voigt language.
$MosaicityText = @'
\subsection{Mosaicity}
\label{sec:mosaicity}
The mosaic picture is most easily understood by comparing the three orientational limits introduced in Fig.~\ref{fig:intro_single_image}, Fig.~\ref{fig:intro_3d_recip}, and Fig.~\ref{fig:intro_2d_recip}. For a perfect single crystal (Fig.~\ref{fig:intro_single_image}), a reflection carries its full weight at a single Bragg spot. For a 3D powder (Fig.~\ref{fig:intro_3d_recip}), random crystallite orientations spread that weight uniformly over the Bragg sphere, so the Ewald-sphere intersection gives a circle of equivalent reciprocal-space points and associated exit vectors $\mathbf{k}_f$. A 2D powder (Fig.~\ref{fig:intro_2d_recip}) lies between these limits: the allowed $\mathbf{k}_f$ values still lie on that circle, but out-of-plane mosaicity makes some portions of the circle more probable than others. Mosaicity is therefore treated as a redistribution of the ideal per-reflection intensity over the allowed \(\mathbf{k}_f\) family, rather than as a change to the underlying diffraction condition or structure factor.

\begin{figure}[H]
  \centering
  \includegraphics[width=0.35\linewidth]{figures/mosaic/2d_mosaic.png}
  \caption{Schematic of crystallite layer-normal misorientation (mosaicity) about the surface normal. A distribution of crystallite orientations may form in a thin film.}
  \label{fig:mosaic}
\end{figure}

For a reflection, we work in the \((G_r, G_z)\) cross-section of reciprocal space, where \(G_r\) is the projection of the reciprocal lattice vector onto the plane of the substrate, and \(G_z\) is the component along the surface normal. In this section, the perfect-crystal Bragg spot appears as a point on the Bragg circle. In the full three-dimensional picture, random in-plane rotations generate the circle of equivalent reciprocal-space intersections and associated \(\mathbf{k}_f\) values described above, consistent with the reciprocal-space evolution from Fig.~\ref{fig:intro_single_image} to Fig.~\ref{fig:intro_3d_recip} to Fig.~\ref{fig:intro_2d_recip}. Out-of-plane misorientation then replaces the uniform weighting of that ideal circle by a line density \(I_0 \omega(\Delta\theta)\), where \(I_0\) is the total intensity associated with the reflection before mosaic redistribution.

We describe this out-of-plane mosaicity by a misorientation density \(\omega(\Delta\theta)\), where \(\Delta\theta\) is the crystallite tilt angle relative to the substrate normal. The implemented density is a normalized Gaussian-plus-Lorentzian angular distribution, evaluated in wrapped form on \((-\pi,\pi]\). It is not a pseudo-Voigt peak function: the Gaussian and Lorentzian widths are independent, and the Lorentzian component is used to capture the long tails needed for off-condition specular intensity. The explicit wrapped Gaussian and wrapped Lorentzian forms are given in the supporting information, Sec.~S1.1. We report the Lorentzian full width at half maximum, the Gaussian full width at half maximum, and the relative Lorentzian weight.

These components are related to the full reciprocal lattice vector \(\bm G = (H, K, L)\), but the relationship depends on the crystal symmetry. For a general crystal, \(G_r\) is defined as the magnitude of the projection of \(\bm G\) onto the plane, and \(G_z\) is the component along the normal direction. The mixed Gaussian-plus-Lorentzian form is motivated by how different regions of the detector image sample \(\omega\). Off-specular reflections with \(G_r\neq 0\) are spread by random in-plane rotation around an azimuthal ring, so their observed widths are governed mainly by the core of the misorientation distribution. Specular \((00L)\) reflections, however, remain concentrated near the \(Q_z\) axis rather than being diluted around that ring. Consequently, even weak tail probability can remain visible in the specular region, allowing intensity from misoriented crystallites to appear at a nominal \(\theta_i\) where a perfectly aligned crystallite would be off condition. The Lorentzian component is therefore introduced to capture the long tails needed to reproduce the persistence of multiple specular reflections at a single nominal incident condition, beyond what beam divergence alone would provide.

Figure~\ref{fig:mosaic_combo} summarizes how this reciprocal-space broadening appears in the $\{G_r,G_z\}$ plane and how it maps onto characteristic detector-space features for in-plane and specular conditions.
\begin{figure}[H]
  \centering
  \captionsetup[subfigure]{list=false,labelsep=none}

  \begin{subfigure}[t]{0.48\linewidth}
    \centering
    \paneltagged{(a)}{\input{figures/mosaic/mosaic_bragg_inplane}}
    \phantomcaption
    \label{fig:mosaic_combo:schem_inplane}
  \end{subfigure}\hfill
  \begin{subfigure}[t]{0.48\linewidth}
    \centering
    \paneltagged{(b)}{\input{figures/mosaic/mosaic_bragg_specular}}
    \phantomcaption
    \label{fig:mosaic_combo:schem_specular}
  \end{subfigure}

  \vspace{0.6em}

  \begin{subfigure}[t]{0.48\linewidth}
    \centering
    \paneltagged{(c)}{\includegraphics[width=0.85\linewidth]{mosaic/inplane_detector_band.png}}
    \phantomcaption
    \label{fig:mosaic_combo:img_inplane}
  \end{subfigure}\hfill
  \begin{subfigure}[t]{0.48\linewidth}
    \centering
    \paneltagged{(d)}{\includegraphics[width=0.85\linewidth]{mosaic/specular_detector_cap.png}}
    \phantomcaption
    \label{fig:mosaic_combo:img_specular}
  \end{subfigure}

  \caption{Mosaic broadening viewed in the $\{G_r,G_z\}$ plane (a,b) and its detector-space manifestation (c,d). Intensity is redistributed along the Bragg circle with line density $I_0\,\omega(\Delta\theta)$. The in-plane condition with $G_r\neq 0$ (a,c) yields two arcs of reflection, while the specular reflection with $G_r=0$ (b,d) concentrates intensity near the polar cap, forming a single arc.}
  \label{fig:mosaic_combo}
\end{figure}

Random in-plane rotations about the film normal revolve that line density about the \(G_z\) axis, generating an axially symmetric distribution on the Bragg sphere. Let \(\vartheta\) denote the polar angle on that sphere, and let \(\vartheta_B\) denote the Bragg position for the reflection, so that the mosaic misorientation is \(\Delta\theta=\vartheta-\vartheta_B\).

We normalize the corresponding Bragg-sphere surface density \(\rho(\vartheta)\) so that \(\int \rho(\vartheta)\,dA = I_0\), yielding
\begin{equation}
\rho(\vartheta)=\frac{I_0}{2\pi G^2\sin\vartheta}\,\omega(\vartheta-\vartheta_B)  \qquad 0<\vartheta<\pi,
  \label{eq:mosaic_rho_maintext}
\end{equation}
where \(G \equiv |\mathbf{G}|\) is the magnitude of the reciprocal-lattice vector, i.e. the Bragg-sphere radius for the reflection. The factor \(1/\sin\vartheta\) is the Jacobian for converting the one-dimensional tilt distribution \(\omega\) into a surface density. This surface density supplies the weights used to distribute the ideal intensity \(I_0\) over the neighboring \(\mathbf{k}_f\) rays generated by misoriented crystallites.

The reciprocal-space consequences appear on an area detector in Fig.~\ref{fig:mosaic_detector_example}. Strong out-of-plane mosaicity concentrates specular intensity near discrete $G_z$ values at $G_r=0$ (region A), while random in-plane orientation distributes in-plane reflections uniformly in azimuth about $G_z$, producing ring-like features (region B).

\begin{figure}[H]
  \centering
  \includegraphics[width=0.3\linewidth]{mosaic/pbi2_waxs.png}
  \caption{Representative log-scale WAXS pattern from a layered 2D-powder film. Region A: multiple specular reflections are visible, although the idealized picture would suggest only one; the lowest-$Q_z$ specular peak exhibits a star-like shape. Region B: in-plane scattering.}
  \label{fig:mosaic_detector_example}
\end{figure}

In the in-plane region (Fig.~\ref{fig:mosaic_detector_example}B), the Ewald sphere intersects the broadened Bragg-sphere feature along an extended band. Azimuthal averaging then produces band-like scattering whose radial width and line shape are set primarily by the Gaussian core of $\omega$ and by the Jacobian factor $1/\sin\vartheta$ in Eq.~\eqref{eq:mosaic_rho_maintext}. In the specular region (Fig.~\ref{fig:mosaic_detector_example}A), the same mosaic spread produces cap-like broadening about the specular reflections. More than one specular peak is visible in region A, even though the idealized specular picture would suggest only a single peak, and the lowest-$Q_z$ specular peak in particular exhibits a star-like profile rather than purely isotropic broadening. This shape is attributed to the finite effective thickness of the Ewald sphere, set by beam divergence and related resolution effects, which becomes comparatively more important for smaller reciprocal-lattice magnitudes \(G\). In addition, small rotations of the Ewald sphere produce smaller positional redistributions closer to the origin, so the broadening is concentrated mainly along \(q_z\) rather than appearing as strong azimuthal spreading. These off-condition specular contributions arise from crystallites whose layer normals are tilted by \(\Delta\theta\) away from the mean. Because the redistributed intensity remains concentrated near the \(Q_z\) axis, the specular region is much more sensitive than the in-plane arcs to the tails of \(\omega\); it therefore provides the primary constraint on the Lorentzian component, with only weak additional variation from the geometric factor in Eq.~\eqref{eq:mosaic_rho_maintext}.
'@
Write-TextFile "sections/mosaicity_texture.tex" $MosaicityText

# 4. Replace the workflow table and explanatory text.
$WorkflowText = @'
\section{Refinement workflow}

Because the forward model combines beam phase space, detector geometry, sample alignment, mosaicity, and crystallographic intensity within a single image calculation, a fully global refinement from arbitrary starting values would lead to strong correlations between instrumental and sample-specific parameters. We therefore use a staged refinement strategy. Each stage uses the detector-space observable that is most diagnostic for that parameter class before the next class of parameters is introduced. Beam and detector terms first establish the fixed experimental geometry shared across measurements. Sample alignment then determines where the reflections appear on the detector. With the reflection positions established, mosaicity is constrained by local line shape, ordered structure by selected Bragg intensities, and stacking disorder by selected rod profiles. The workflow is summarized in Table~\ref{tab:refinement_workflow}.

\begin{table}[!ht]
  \centering
  \caption{Staged refinement workflow. All sample images are dark-subtracted before the listed observables are formed.}
  \label{tab:refinement_workflow}
  \scriptsize
  \setlength{\tabcolsep}{3pt}
  \renewcommand{\arraystretch}{1.08}
  \begin{tabularx}{\linewidth}{@{}c >{\raggedright\arraybackslash}p{2.55cm} >{\raggedright\arraybackslash}X >{\raggedright\arraybackslash}X >{\raggedright\arraybackslash}p{2.9cm}@{}}
    \toprule
    Step & Stage & Data & Parameters refined & Primary information \\
    \midrule
    1 &
    Beam characterization &
    Direct-beam images at several detector distances &
    Beam widths $w_x$, $w_z$ and divergences $\Delta\theta_x$, $\Delta\theta_z$ &
    Incident phase space \\
    2 &
    Detector geometry calibration &
    Powder calibrant image &
    Detector distance $D$, detector tilts $(\beta,\gamma)$, in-plane rotation $\chi$, and beam center $(x_0,y_0)$ &
    Detector mapping \\
    3 &
    Sample alignment and goniometer misalignment &
    Indexed reflection centers from sample images &
    Sample geometry $(\theta_i,\delta,z_B,z_S)$, goniometer misalignment $(\alpha,\psi)$, and film dimensions $(W,H,t)$ &
    Detector-space peak positions \\
    4 &
    Mosaicity/profile refinement &
    Selected local detector ROIs and local $I(\phi)$ profiles &
    Gaussian-plus-Lorentzian mosaic/profile parameters, with geometry fixed &
    Center-aligned profile shapes and specular tails \\
    5 &
    Ordered-structure refinement &
    Selected detector-space Bragg ROIs from multiple dark-subtracted images &
    Image scales and ordered-structure parameters entering Eq.~\eqref{eq:structure_factor}, including occupancies $o_a$, atomic positions $\mathbf{r}_a$, static displacements $\Delta\mathbf{r}_a$, and anisotropic Debye--Waller terms $\mathbf{U}$ &
    Relative ROI-integrated Bragg intensities \\
    6 &
    Disorder refinement &
    Selected $Q_r/Q_z$ rod profiles from caked signal and normalization fields &
    Stacking-fault or slip probability, optional finite-stack or mixture terms, and declared scale/background terms &
    Diffuse $Q_z$ redistribution along the selected rod \\
    \bottomrule
  \end{tabularx}
\end{table}

The first two stages isolate the instrumental contribution to the measured image. Direct-beam images collected at several detector distances determine the incident-beam widths and divergences used in the forward model. These quantities define the baseline phase-space spread of the incoming beam and therefore the instrumental broadening that would be present even for an ideal sample. Detector distance, tilts, in-plane rotation, and beam center are then refined from the hBN Debye--Scherrer rings. This calibration fixes the mapping from reciprocal-space intersections to detector coordinates independently of the sample, so that later discrepancies in peak position or line shape are not absorbed spuriously into sample parameters.

With the instrumental terms fixed, refinement proceeds to the sample geometry. For each sample image, alignment and goniometer misalignment are determined from indexed Bragg-peak positions rather than from global intensities, because feature location is the most direct signature of geometric error. Reflections spanning both the specular and off-specular regions are included so that the fit is constrained simultaneously by the central $Q_z$-dominated features and by the off-axis intersections of the reciprocal-space rings. This step establishes the actual incidence condition and illuminated geometry of the experiment, which must be known before peak widths and intensities can be interpreted physically.

Mosaicity is refined only after the reflection positions have been fixed, so that the remaining variation in line shape can be attributed to crystallite misorientation rather than to geometric offset. The fit uses selected local detector regions around indexed reflections and compares measured and simulated local profiles after center alignment. When multiple incidence settings are available, they share the same Gaussian-plus-Lorentzian mosaic density. This model is not a pseudo-Voigt peak approximation: the Gaussian and Lorentzian components have independent widths and together describe a wrapped angular distribution. Off-specular arcs constrain the Gaussian-dominated core width, whereas the persistence and decay of specular intensity constrain the Lorentzian tail more strongly.

Only after the geometric and mosaic terms have converged are the remaining Bragg-intensity variations assigned to ordered structure. The ordered stage uses background-subtracted integrated counts from selected detector-space Bragg ROIs, compared with the simulated detector-carried intensity deposited in those same ROIs. It is therefore a multi-image refinement of relative Bragg intensities, not a full-image pixel-by-pixel refinement. One nuisance scale is allowed for each image to absorb exposure and flux differences, while the shared ordered-structure parameters control the reflection-to-reflection intensity ratios.

Disorder parameters are introduced only after the ordered model has been pushed as far as it can go. At that point the beam, detector, sample geometry, mosaic/profile state, lattice parameters, and ordered intensity baseline are held fixed. The final observable is a selected $Q_r/Q_z$ rod profile formed from caked signal and normalization fields by summing signal and normalization over the selected rod mask before division. The fit changes only the stacking-disorder parameters and explicitly declared nuisance scale or background terms. This separation is essential because diffuse intensity along $Q_z$ near and between Bragg peaks is otherwise easily confounded with average-structure or broadening effects.
'@
Write-TextFile "sections/refinement_workflow.tex" $WorkflowText

# 5. Fill Section 5 with a less detailed ordered-film result and placeholder figures.
$OrderedText = @'
\section{Results: ordered films}

We first apply the staged workflow to ordered MBE-grown Bi$_2$Te$_3$ and Bi$_2$Se$_3$ films. These samples provide the ordered-limit check for the model: the detector images contain the specular features and off-specular arcs expected for a 2D oriented powder, but the dominant intensity can be treated without adding an explicit stacking-disorder term. The goal of this section is therefore not to re-solve the crystal structures from scratch. It is to test whether the same detector-space workflow can recover geometry, alignment, mosaic broadening, and relative ordered Bragg intensities in two related layered films.

\begin{figure}[H]
  \centering
  \begin{subfigure}[t]{0.48\linewidth}
    \centering
    \maybeincludecompact[width=\linewidth]{figures/results_ordered/bite_detector_fit.png}
    \caption{}
    \label{fig:ordered_detector_fits:bite}
  \end{subfigure}\hfill
  \begin{subfigure}[t]{0.48\linewidth}
    \centering
    \maybeincludecompact[width=\linewidth]{figures/results_ordered/bise_detector_fit.png}
    \caption{}
    \label{fig:ordered_detector_fits:bise}
  \end{subfigure}

  \vspace{0.5em}

  \begin{subfigure}[t]{0.48\linewidth}
    \centering
    \maybeincludecompact[width=\linewidth]{figures/results_ordered/ordered_profile_examples.png}
    \caption{}
    \label{fig:ordered_detector_fits:profiles}
  \end{subfigure}\hfill
  \begin{subfigure}[t]{0.48\linewidth}
    \centering
    \maybeincludecompact[width=\linewidth]{figures/results_ordered/ordered_qz_checks.png}
    \caption{}
    \label{fig:ordered_detector_fits:qz}
  \end{subfigure}
  \caption{Placeholder layout for the ordered-film result. (a) Bi$_2$Te$_3$ measured/simulated/residual detector comparison. (b) Bi$_2$Se$_3$ measured/simulated/residual detector comparison. (c) Local mosaic/profile checks from selected detector ROIs. (d) Reciprocal-space or $Q_z$ checks used after the detector-space fit.}
  \label{fig:ordered_detector_fits}
\end{figure}

Figure~\ref{fig:ordered_detector_fits} will show the ordered-film detector comparisons. The geometry stage is judged first by feature placement. A successful solution must place the specular region and the off-specular arcs simultaneously; improving one feature class while displacing the other is treated as residual geometric error rather than structural information. Once the detector registration is fixed, the remaining local broadening is interpreted as sample-specific mosaicity.

Mosaicity is constrained from selected local detector regions rather than from the full image intensity. Specular caps and off-specular arcs are reduced to local intensity-versus-angle profiles, and measured and simulated profiles are compared after their centers are aligned. This keeps the mosaic stage focused on profile shape and prevents it from absorbing the inter-peak intensity ratios reserved for the ordered-structure refinement. The off-specular arcs primarily constrain the Gaussian core of the profile, while the persistence of specular intensity constrains the Lorentzian tail.

The ordered-structure stage is entered only after the beam, detector, sample-alignment, and mosaic terms have been fixed. The fitted observables are background-subtracted integrated counts in selected detector-space Bragg ROIs, compared with the simulated detector-carried intensity deposited in the same ROIs. One nuisance scale is allowed for each image to account for exposure and flux differences. The ordered refinement is therefore a constrained multi-image refinement of relative Bragg intensities, not a full-image pixel fit and not an unconstrained crystallographic structure solution.

The resulting ordered model is checked against reciprocal-space cuts and against the full detector-space morphology. Agreement in both views indicates that the ordered description is sufficient for these films within the resolution of the present workflow. The important result is not that Bi$_2$Te$_3$ and Bi$_2$Se$_3$ return identical parameters, but that the same refinement hierarchy remains stable in both systems. This ordered benchmark defines the baseline tested by the PbI$_2$ disorder case below.
'@
Write-TextFile "sections/results_ordered.tex" $OrderedText

# 6. Fill Section 6 with the PbI2 disorder refinement, using the no-correlation analytical appendix and placeholder figures.
$PbI2Text = @'
\section{Results: diffuse scattering in PbI\texorpdfstring{$_2$}{2}}

We next apply the workflow to CVD-grown PbI$_2$ films. PbI$_2$ is the disorder-sensitive case because the measured image contains diffuse intensity along selected $Q_z$ rods that is not captured by the ordered baseline alone. The analysis therefore begins in the same way as for the ordered films: beam and detector terms are fixed, sample alignment is determined from detector-space feature positions, mosaic/profile parameters are constrained from local line shapes, and the ordered PbI$_2$ intensity model is pushed as far as it can go. The stacking-fault model is introduced only after that ordered baseline leaves structured residual intensity along the selected rod direction.

\begin{figure}[H]
  \centering
  \begin{subfigure}[t]{0.48\linewidth}
    \centering
    \maybeincludecompact[width=\linewidth]{figures/results_pbi2/pbi2_detector_selected_rod.png}
    \caption{}
    \label{fig:pbi2_disorder_fit:selectedrod}
  \end{subfigure}\hfill
  \begin{subfigure}[t]{0.48\linewidth}
    \centering
    \maybeincludecompact[width=\linewidth]{figures/results_pbi2/pbi2_ordered_baseline_profile.png}
    \caption{}
    \label{fig:pbi2_disorder_fit:ordered}
  \end{subfigure}

  \vspace{0.5em}

  \begin{subfigure}[t]{0.48\linewidth}
    \centering
    \maybeincludecompact[width=\linewidth]{figures/results_pbi2/pbi2_disorder_profile_fit.png}
    \caption{}
    \label{fig:pbi2_disorder_fit:disorder}
  \end{subfigure}\hfill
  \begin{subfigure}[t]{0.48\linewidth}
    \centering
    \maybeincludecompact[width=\linewidth]{figures/results_pbi2/pbi2_before_after_residuals.png}
    \caption{}
    \label{fig:pbi2_disorder_fit:residuals}
  \end{subfigure}
  \caption{Placeholder layout for the PbI$_2$ disorder result. (a) Detector image or caked image with the selected $Q_r/Q_z$ rod ROI overlaid. (b) Ordered-baseline profile and residual. (c) Selected-rod profile after the no-correlation analytical stacking-fault fit. (d) Residual comparison before and after adding the disorder term.}
  \label{fig:pbi2_disorder_fit}
\end{figure}

The PbI$_2$ model used here is not a generic Bragg-sphere or cylinder picture. The active PbI$_2$ structural model first generates ordered rod base curves for the selected in-plane family. The no-correlation analytical stacking-fault model in the supporting information then redistributes that ordered intensity along the stacking coordinate. In the main text we write the result schematically as
\begin{equation}
I_{hk}(L)=\mathcal{A}F_{hk}^{2}(L)R_{hk}(L;p,N,\ldots),
\label{eq:pbi2_rod_main}
\end{equation}
where $F_{hk}^{2}(L)$ is the ordered PbI$_2$ rod intensity, $R_{hk}$ is the analytical stacking-fault correction, $p$ is the reported slip or fault parameter, and $N$ is retained only when an effective finite-stack length is used. The derivation and conventions are kept in the supporting information so the main text can stay focused on the detector-space refinement.

The disorder observable is built from the caked detector fields. For each caked bin, the scattering magnitude and selected-rod coordinates are
\begin{equation}
Q=\frac{4\pi}{\lambda}\sin\!\left(\frac{2\theta}{2}\right),
\qquad
Q_r=|\sin\phi|Q,
\qquad
Q_z=\cos\phi\,Q.
\label{eq:pbi2_selected_coords}
\end{equation}
A rod mask keeps bins satisfying $|Q_r-Q_{r,0}|\le\Delta Q_r$ and the chosen $Q_z$ bounds, with one detector branch used for the default fit and the opposite branch held as a validation profile. If $S_{ij}$ and $N_{ij}$ are the caked signal and normalization fields, the measured rod profile is
\begin{equation}
I_j^{\mathrm{rod}}=\frac{\sum_i m_{ij}S_{ij}}{\sum_i m_{ij}N_{ij}},
\label{eq:pbi2_rod_profile}
\end{equation}
for bins with positive selected normalization. Signal and normalization are summed before division; already normalized pixels are not averaged.

The selected-rod profile is fit directly. Beam, detector geometry, sample alignment, mosaic/profile state, lattice constants, and the ordered PbI$_2$ baseline are held fixed. Known Bragg positions on the retained branch define the profile locations. The local peak response is the fixed or tightly constrained Gaussian-plus-Lorentzian response inherited from the upstream mosaic and instrumental state, not an independently released pseudo-Voigt peak model. The free terms are the stacking-fault parameter or parameters, any declared finite-stack or mixture terms, and a small set of explicit scale/background nuisance terms. Peak areas are not released independently, because that would allow the line-shape model to absorb the between-peak diffuse intensity that is meant to constrain stacking disorder.

Figure~\ref{fig:pbi2_disorder_fit} will show the selected-rod comparison. The ordered baseline should capture the principal Bragg locations but leave systematic diffuse intensity along $Q_z$. Adding the analytical stacking-fault term should reduce that selected-rod residual while leaving the upstream detector-space agreement intact. The fitted values should therefore be interpreted as effective stacking-disorder descriptors within the chosen no-correlation analytical model, not as a unique reconstruction of every layer sequence in the film.
'@
Write-TextFile "sections/results_diffuse_pbi2.tex" $PbI2Text

# 7. Update the front part of the supporting information. The existing no-correlation stacking-fault appendix is intentionally left alone.
$SiWorkflow = @'
\section{Staged refinement workflow (expanded)}
\label{sec:si_workflow}

\begin{enumerate}
  \item \textbf{Beam characterization (direct beam).}
  Acquire direct-beam images at several detector distances. Fit the spot position and shape versus distance to determine the incident-beam widths $(w_x,w_z)$ and Gaussian divergences $(\Delta\theta_x,\Delta\theta_z)$ that set the instrument-limited broadening.

  \item \textbf{Detector geometry calibration (3D powder standard).}
  Measure a polycrystalline hBN calibrant and subtract the detector dark frame. Fit multiple Debye--Scherrer rings in detector coordinates and refine detector distance, detector tilts $(\beta,\gamma)$, in-plane detector rotation $\chi$, and beam center $(x_0,y_0)$.

  \item \textbf{Sample alignment and goniometer misalignment.}
  For each dark-subtracted sample image, use indexed Bragg-peak centers rather than full-image intensity. With detector parameters fixed, refine sample alignment by minimizing detector-space residuals between measured and simulated peak positions spanning both specular and off-specular regions. Refine $(\theta_i,\delta,z_B,z_S)$ and the goniometer-axis misalignment rotations $(\alpha,\psi)$; include film dimensions $(W,H)$ and thickness $t$ to weight footprint and absorption.

  \item \textbf{Mosaicity/profile refinement.}
  With geometry fixed, compare selected local detector ROIs or local $I(\phi)$ profiles after center alignment. The shared profile model is a wrapped Gaussian-plus-Lorentzian angular distribution, not a pseudo-Voigt common-width peak approximation. Off-specular arcs mainly constrain the Gaussian core, while off-condition specular intensity constrains the Lorentzian tail. Report Lorentzian FWHM, Gaussian FWHM, and the relative Lorentzian weight.

  \item \textbf{Ordered-structure refinement.}
  With geometry and mosaicity fixed, refine the ordered intensity model against background-subtracted integrated counts in selected detector-space Bragg ROIs from multiple dark-subtracted images. The corresponding prediction is the simulated detector-carried intensity deposited in those same ROIs. Use one nuisance scale per image and physically constrained ordered-structure parameters.

  \item \textbf{Disorder refinement.}
  After the ordered model converges, introduce stacking-disorder parameters only through selected $Q_r/Q_z$ rod profiles. The measured profile is formed from caked signal and normalization fields by summing signal and normalization over the selected rod mask before division. Geometry, detector calibration, beam terms, mosaicity, lattice constants, and the ordered baseline remain fixed; only stacking-disorder parameters and declared scale/background terms are refined.
\end{enumerate}

All detector images are dark-subtracted before fitting. Any additional preprocessing (flat-field, polarization, solid-angle, or detector-efficiency corrections) should either be applied consistently to all images before refinement or stated explicitly if omitted. We recommend stage-specific uncertainty estimation by repeated constrained refits: resample the calibrant points for detector geometry, indexed peak lists for sample alignment, local reflection regions for mosaicity, accepted Bragg ROIs for ordered intensity, and selected rod bins for disorder. Report the standard deviation of the accepted solutions and propagate parameters to the next stage only after the preceding stage is stable.
'@

$SiMosaic = @'
\subsection{Wrapped mosaic distribution}
\label{subsec:si_wrapped_mosaic}

In the main text we describe out-of-plane mosaicity by a misorientation density $\omega(\Delta\theta)$ in the crystallite tilt angle $\Delta\theta$ relative to the substrate normal. Since $\Delta\theta$ is an orientation angle, $\Delta\theta$ and $\Delta\theta+2\pi$ represent the same physical state. Accordingly, $\omega$ is treated as a $2\pi$-periodic probability density on $\Delta\theta\in(-\pi,\pi]$.

The implemented profile is a wrapped Gaussian plus a wrapped Lorentzian,
\[
  \omega_{\mathrm w}(\Delta\theta;\eta,\Gamma,\sigma)
  =\eta\,L_{\mathrm w}(\Delta\theta;\Gamma)+(1-\eta)\,G_{\mathrm w}(\Delta\theta;\sigma),
  \qquad 0\le \eta \le 1.
\]
This is not a pseudo-Voigt constraint: the Lorentzian half-width $\Gamma$ and Gaussian standard deviation $\sigma$ are independent. The wrapped Lorentzian and wrapped Gaussian are
\[
  L_{\mathrm w}(\Delta\theta;\Gamma)=
  \sum_{m=-\infty}^{\infty}\frac{1}{\pi}\frac{\Gamma}{(\Delta\theta+2\pi m)^2+\Gamma^2}
  =\frac{1}{2\pi}\,\frac{\sinh\Gamma}{\cosh\Gamma-\cos\Delta\theta},
\]
\[
  \begin{aligned}
    G_{\mathrm w}(\Delta\theta;\sigma)
    &= \sum_{m=-\infty}^{\infty}\frac{1}{\sqrt{2\pi}\sigma}
       \exp\!\left[-\frac{(\Delta\theta+2\pi m)^2}{2\sigma^2}\right] \\
    &= \frac{1}{2\pi}\!\left[
         1+2\sum_{n=1}^{\infty}e^{-n^2\sigma^2/2}\cos(n\Delta\theta)
       \right].
  \end{aligned}
\]
Both components integrate to unity over $(-\pi,\pi]$, so $\omega_{\mathrm w}$ is normalized. The reported Lorentzian FWHM is $2\Gamma$, and the reported Gaussian FWHM is $2\sqrt{2\ln 2}\,\sigma$. The local small-width limit recovers the usual line-shape widths, but the refinement and normalization are defined by the wrapped functions above.

For a reflection with Bragg-sphere radius $G \equiv |\mathbf G|$, mosaicity redistributes intensity in polar angle $\vartheta$ with line density $I_0\,\omega_{\mathrm w}(\vartheta-\vartheta_B)\,d\vartheta$, where $\vartheta_B$ is the Bragg position for that reflection. Random in-plane rotations about the film normal revolve this line density about the $G_z$ axis, yielding an axially symmetric surface density $\rho(\vartheta)$. With area element $dA=2\pi G^2\sin\vartheta\,d\vartheta$, conservation of intensity gives
\[
  \rho(\vartheta)=\frac{I_0}{2\pi G^2\sin\vartheta}\,\omega_{\mathrm w}(\vartheta-\vartheta_B),
  \qquad 0<\vartheta<\pi,
\]
as used in the main text.
'@

$SiObs = @'
\subsection{Detector-derived ordered and disorder observables}
\label{subsec:si_detector_derived_objectives}

The detector-space forward model predicts full images, but the inverse problems use stage-specific observables. In the ordered-structure stage, the measured quantity for ROI $i$ in image $m$ is the background-subtracted detector count
\[
  y_{mi}=\sum_{(u,v)\in\Omega_{mi}}\left[I_m^{\mathrm{meas}}(u,v)-b_{mi}(u,v)\right],
\]
where $\Omega_{mi}$ is the selected detector-space Bragg ROI and $b_{mi}$ is the local background model. The corresponding prediction is the simulated detector-carried intensity deposited in the same ROI,
\[
  \mu_{mi}=\sum_{j\in\mathcal{R}_{mi}} w_j,
\]
with geometry, beam terms, and mosaicity fixed. One nuisance scale per image accounts for exposure and flux differences. This makes the ordered stage a multi-image ROI-integrated Bragg-intensity refinement, not a full-image pixel objective.

The PbI$_2$ disorder refinement is a final-stage selected-profile fit, not a second global image refinement. The upstream beam, detector, sample alignment, mosaic/profile parameters, lattice constants, and ordered PbI$_2$ baseline are fixed before this stage starts. The detector image is first caked into a signal field $S(\phi,2\theta)$ and a normalization field $N(\phi,2\theta)$ using the calibrated detector geometry. For each caked bin,
\[
  Q=\frac{4\pi}{\lambda}\sin\!\left(\frac{2\theta}{2}\right),
  \qquad
  Q_r=|\sin\phi|Q,
  \qquad
  Q_z=\cos\phi\,Q.
\]
A selected rod with in-plane radius $Q_{r,0}$ is retained when
\[
  |Q_r-Q_{r,0}|\le \Delta Q_r,
  \qquad
  Q_{z,\min}\le Q_z\le Q_{z,\max}.
\]
A branch selector may be applied after this reciprocal-space mask so that one branch is used for the default fit and the symmetry-related branch is retained for validation.

Let $S_{ij}$ and $N_{ij}$ denote the caked signal and normalization fields, and let $m_{ij}$ denote the selected-rod mask. The measured profile is
\[
  I_j^{\mathrm{rod}}=\frac{\sum_i m_{ij}S_{ij}}{\sum_i m_{ij}N_{ij}},
\]
for bins with positive selected normalization. Signal and normalization are therefore summed before division. This prevents the final trace from becoming a sum of already normalized pixels and keeps the observable tied to the detector-space calibration.

The model profile is evaluated along the same selected branch. In compact notation,
\[
  M_j(\boldsymbol{\theta}_{\mathrm{dis}})
  =B(x_j)+s\,[K*I_{hk}^{\mathrm{nc}}(L;\boldsymbol{\theta}_{\mathrm{dis}})]_j,
\]
where $x_j$ is the profile coordinate, $L$ is the corresponding stacking coordinate on the selected branch, $B$ is a low-order background, $s$ is a global scale, $K$ is the fixed detector/profile broadening kernel, and $I_{hk}^{\mathrm{nc}}$ is the no-correlation analytical stacking intensity from Sec.~\ref{sec:nocorr}. When an explicit closed-form broadening kernel is used, $K$ is written as a Gaussian-plus-Lorentzian kernel with widths fixed by the upstream resolution and mosaic/profile state or declared before the disorder fit. It is not used to release independent peak areas.

The disorder objective is evaluated only over the retained profile bins,
\[
  \chi^2_{\mathrm{dis}}(\boldsymbol{\theta}_{\mathrm{dis}},s,B)
  =\sum_{j\in\mathcal J}\rho\!\left(
  \frac{I_j^{\mathrm{rod}}-M_j(\boldsymbol{\theta}_{\mathrm{dis}})}{\sigma_j}
  \right),
\]
where $\rho$ may be a least-squares or robust loss and $\mathcal J$ is the retained $Q_z$ interval. The known Bragg locations on the selected branch are inherited from the fixed detector geometry and ordered model. Peak amplitudes are not fit independently before the stacking model is applied; otherwise the diffuse between-peak intensity would already have been absorbed by the preprocessing.
'@

Update-TextFile "2D_Supplemental/SI_failure_modes.tex" {
  param($Text)
  $SiFront = $SiWorkflow.TrimEnd() + "`n`n" + $SiMosaic.TrimEnd() + "`n`n"
  $Text = Replace-BetweenLiterals $Text "\section{Staged refinement workflow (expanded)}" "\subsection{Wave propagation, refraction, and absorption}" $SiFront "SI expanded workflow and wrapped mosaic distribution"

  $Marker = "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%`n% 1  Material background"
  $MarkerIndex = $Text.IndexOf($Marker)
  if ($MarkerIndex -lt 0) { throw "Could not find material-background marker for SI insertion." }

  $ObsStart = -1
  $ObsCandidates = @(
    '\subsection{Detector-derived ordered and disorder observables}',
    '\subsection{Selected-\texorpdfstring{$Q_r/Q_z$}{Qr/Qz} rod profile for PbI\texorpdfstring{$_2$}{2} disorder}'
  )
  foreach ($Candidate in $ObsCandidates) {
    $CandidateIndex = $Text.IndexOf($Candidate)
    if (($CandidateIndex -ge 0) -and ($CandidateIndex -lt $MarkerIndex)) {
      if (($ObsStart -lt 0) -or ($CandidateIndex -lt $ObsStart)) { $ObsStart = $CandidateIndex }
    }
  }

  if ($ObsStart -ge 0) {
    $Text = $Text.Substring(0, $ObsStart) + $SiObs.TrimEnd() + "`n`n" + $Text.Substring($MarkerIndex)
  } else {
    $Text = $Text.Insert($MarkerIndex, $SiObs.TrimEnd() + "`n`n")
  }
  return $Text
}

Write-Host "Patch applied. Backups were written next to edited files with suffix .bak-$Timestamp."
Write-Host "Edited: sections/introduction.tex, sections/modelling_methods.tex, sections/mosaicity_texture.tex, sections/refinement_workflow.tex, sections/results_ordered.tex, sections/results_diffuse_pbi2.tex, 2D_Supplemental/SI_failure_modes.tex"
