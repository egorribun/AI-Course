# Project: Deep Learning Course Verification & Remediation

## Architecture
- **Curriculum Scope**: 28 self-contained interactive lecture HTML pages (`lectures/00-intro-ml.html` .. `lectures/27-actor-critic.html`) and central portal `index.html`.
- **Reference Basis**: State University of Management (GUU, 2026) Deep Learning exam syllabus (`dl_guu-dl_26/`).
- **Core Technology Stack**: Static HTML5, CSS3, MathJax 3.2.2 (SVG/TeX engine), Python 3.10+ / PyTorch 2.x executable snippets.
- **Structural Contract per Lecture**:
  * Top navigation backlink (`← К оглавлению курса`)
  * Header metadata (`.pill` badges for duration, QA count, task count)
  * Theoretical Sections with MathJax derivations and ASCII diagrams
  * Interactive Q&A block: «🎯 Препод спросит» ($\ge 10$ questions per lecture in `<details class="qa">`)
  * Micro-tasks block: «📝 Микро-задачи» ($\ge 6$ tasks per lecture in `<div class="task">` with `<details class="sol">`)
  * Cheat-sheet block: «⚡ Ответ за 3 минуты» (`<div class="cheat">`)
  * Bottom sequential navigation bar (`.navrow` with Prev/Next links)

## Feature Inventory
| # | Feature / Exam Ticket | Description | Milestone | Source |
|---|----------------------|-------------|-----------|--------|
| 1 | Foundations & Backprop (Ticket 1) | MLP, activations, vanishing gradients, Cybenko theorem, 4 backprop equations | M1, M2 | Survey (L00, L01) |
| 2 | Autodiff & PINN (Ticket 2) | DAG, forward/reverse autodiff, PINN PDE residual loss, $C^2$ activations | M1, M2 | Survey (L02) |
| 3 | Loss Functions & MLE (Ticket 3) | MSE (Gaussian), MAE (Laplace), BCE/CE, NLL minimization, MAP / L2 weight decay | M1, M2 | Survey (L03) |
| 4 | CNN Layers (Ticket 4) | Convolutions, tensor dimensions, receptive field, BatchNorm, 1x1 conv, pooling | M1, M2 | Survey (L04) |
| 5 | CNN Architectures (Ticket 5) | LeNet to ResNet/ViT, skip connections $\frac{\partial L}{\partial x}$, transfer learning matrix | M1, M2 | Survey (L05) |
| 6 | Optimizers & Matrix Calculus (Ticket 6) | SGD, Momentum, NAG, RMSProp, Adam bias correction, AdamW, normal equation | M1, M2 | Survey (L06) |
| 7 | Hyperparameters & Tuning (Ticket 7) | Augmentations, Grid/Random search, Bayesian Opt (Gaussian Process, EI/UCB), Hyperband | M1 | Survey (L07) |
| 8 | Metric Learning (Ticket 8) | Siamese networks, Contrastive / Triplet loss with margin, mining, ArcFace | M1 | Survey (L08) |
| 9 | Contrastive & SSL (Ticket 9) | InfoNCE / NT-Xent, SimCLR, MoCo, BYOL/SimSiam collapse avoidance, CLIP | M1, M2 | Survey (L09) |
| 10 | VAE & CVAE (Ticket 10) | ELBO derivation, Gaussian KL analytical form, Reparameterization trick, CVAE | M1, M2 | Survey (L10) |
| 11 | GAN (Ticket 11) | Minimax game, optimal discriminator $D^*$, JSD derivation, WGAN-GP, Mode collapse | M1, M3 | Survey (L11) |
| 12 | Diffusion Models (Ticket 12, part 1) | DDPM forward marginal $q(x_t \vert x_0)$, reverse denoising $L_{simple}$, Latent Diffusion | M1, M3 | Survey (L12) |
| 13 | CV Tasks (Ticket 12, part 2) | Segmentation (U-Net, DeepLab, Dice), Detection (Faster R-CNN, YOLO, mAP), Tracking | M1, M3 | Survey (L13) |
| 14 | RNN, LSTM & biLSTM (Ticket 13) | BPTT gradient vanishing, Constant Error Carousel, 3 gates, biLSTM | M2, M3 | Survey (L14) |
| 15 | Attention & Seq2Seq (Ticket 14) | Information bottleneck, Bahdanau additive vs Luong dot attention, alignment matrix | M1, M3 | Survey (L15) |
| 16 | Transformer Architecture (Ticket 15) | Encoder-Decoder stacks, Multi-Head Attention, Pre/Post-LN, Positional Encoding | M1, M3 | Survey (L16) |
| 17 | Self-Attention Mechanics (Ticket 16) | $Q, K, V$ projections, $\sqrt{d_k}$ scaling variance proof, causal/padding masks | M1, M3 | Survey (L17) |
| 18 | LSTM vs Transformer (Ticket 17) | 8-axis comparative analysis (parallelism, memory $O(n^2)$, inductive bias, KV cache) | M3 | Survey (L18) |
| 19 | Text Preprocessing & Word2vec (Ticket 18) | BPE/SentencePiece subwords, CBOW, Skip-Gram with Negative Sampling (SGNS) | M2, M3 | Survey (L19) |
| 20 | Machine Translation & BLEU (Ticket 19) | Teacher forcing, Beam search decoding, modified $n$-gram precision, Brevity Penalty | M2, M3 | Survey (L20) |
| 21 | Transformer Archetypes (Ticket 20) | Encoder-only (BERT), Decoder-only (GPT), Enc-Dec (T5), Causal vs Bidirectional | M3 | Survey (L21) |
| 22 | RL Foundations & MDP (Ticket 21) | Agent-environment loop, Markov property, Discounted return $G_t$, Policy $\pi$, Value $V, Q$ | M3 | Survey (L22) |
| 23 | Bellman Equations & Optimality (Ticket 22a) | Bellman expectation & optimality equations, Backup diagrams, Banach Contraction | M1, M3 | Survey (L23) |
| 24 | Dynamic Programming & MC in RL (Ticket 22b) | Policy Iteration, Value Iteration, First/Every-visit MC control with Exploring Starts | M2, M3 | Survey (L24) |
| 25 | TD Learning, SARSA & Q-Learning (Ticket 23) | TD error $\delta_t$, SARSA (on-policy) vs Q-learning (off-policy), DQN Replay Buffer | M2, M3 | Survey (L25) |
| 26 | Policy Gradient & REINFORCE (Ticket 24) | Log-derivative trick, Policy Gradient Theorem, Baseline variance reduction, PPO-Clip | M2, M3 | Survey (L26) |
| 27 | Actor-Critic, GAE & SAC (Ticket 25) | Advantage $A(s,a)$, A2C, GAE $\lambda$, Maximum Entropy RL in SAC | M2, M3 | Survey (L27) |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| **M0** | E2E Test Suite Creation | Automated python verification harness checking R1, R2, R3, R4 | none | **DONE** |
| **M1** | Math & LaTeX Remediation | Fix L06 brace, L10 VAE ELBO gap formula, L13 tag bug, HTML entities in math | none | **DONE** |
| **M2** | PyTorch Code Syntax & Execution Fix | Fix unescaped `<` in L14 & L24, raw `>` in L01 & L20, test all snippets | none | **DONE** |
| **M3** | Q&A Content Expansion (57 questions) | Generate and inject 57 high-quality exam questions with answers across 16 lectures (11, 12, 14–27) so all 28 lectures have $\ge 10$ QA | M0 | **DONE** |
| **M4** | E2E Full Pass & Adversarial Hardening | Run 100% test suite, Challenger verification, Forensic Audit | M1, M2, M3 | **DONE** |

## Interface Contracts & Layout
### Code Layout
- Portal: `c:\Users\egorribun\Documents\AI-Course\index.html`
- Lectures: `c:\Users\egorribun\Documents\AI-Course\lectures\00-intro-ml.html` ... `27-actor-critic.html`
- Styles: `c:\Users\egorribun\Documents\AI-Course\style.css` (and embedded `<style>` blocks)
- Reference Material: `c:\Users\egorribun\Documents\AI-Course\dl_guu-dl_26/`
- Test Harness: `c:\Users\egorribun\Documents\AI-Course\tests/`
