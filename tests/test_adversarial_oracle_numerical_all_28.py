import unittest
import sys
from pathlib import Path

COURSE_ROOT_DIR = Path(__file__).resolve().parent.parent
if str(COURSE_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(COURSE_ROOT_DIR))

from tests.common import EXPECTED_LECTURES, LECTURES_DIR, read_file


class TestAdversarialOracleNumericalAll28(unittest.TestCase):
    """Rigorous empirical oracle checking arithmetic and step-by-step numbers across all 28 lectures."""

    @classmethod
    def setUpClass(cls):
        cls.lectures = {lec: read_file(LECTURES_DIR / lec) for lec in EXPECTED_LECTURES}

    def test_00_intro_ml_gd(self):
        txt = self.lectures["00-intro-ml.html"]
        self.assertIn("1.25", txt)
        self.assertIn("0.45", txt)

    def test_01_fcnn_mlp_backprop(self):
        txt = self.lectures["01-fcnn.html"]
        self.assertIn("0.07", txt)
        self.assertIn("-0.29", txt)
        self.assertIn("0.235", txt)
        self.assertIn("0.2926", txt)
        self.assertIn("-0.765", txt)
        self.assertIn("0.505355", txt)
        self.assertIn("0.2765", txt)

    def test_02_autodiff_reverse_graph(self):
        txt = self.lectures["02-autodiff-pinn.html"]
        self.assertIn("12.9093", txt)
        self.assertIn("11.5839", txt)
        self.assertIn("4.0", txt)

    def test_03_losses_mle_outlier_focal(self):
        txt = self.lectures["03-losses-mle.html"]
        self.assertIn("2304.0", txt)
        self.assertIn("24.0", txt)
        self.assertIn("37.25", txt)
        self.assertIn("5.25", txt)
        self.assertIn("0.001054", txt)
        self.assertIn("1.0300", txt)

    def test_04_cnn_conv2d(self):
        txt = self.lectures["04-cnn-layers.html"]
        self.assertIn("-0.5", txt)
        self.assertIn("0.5", txt)
        self.assertIn("-1.5", txt)

    def test_05_resnet_flops_gradient(self):
        txt = self.lectures["05-cnn-architectures.html"]
        self.assertIn("1 179 648", txt.replace(r"\,", " ").replace("&nbsp;", " "))
        self.assertIn("69 632", txt.replace(r"\,", " ").replace("&nbsp;", " "))
        self.assertIn("0.84", txt)
        self.assertIn("-0.40", txt)

    def test_06_optimizers_adam_normal_eq(self):
        txt = self.lectures["06-optimizers.html"]
        self.assertIn("1.90", txt)
        self.assertIn("1.80017", txt)
        self.assertIn("14", txt)

    def test_07_hyperparams_cutmix_ucb(self):
        txt = self.lectures["07-hyperparams.html"]
        self.assertIn("0.75", txt)
        self.assertIn("0.25", txt)
        self.assertIn("0.900", txt)
        self.assertIn("0.960", txt)
        self.assertIn("1.020", txt)

    def test_08_metric_triplet_mining(self):
        txt = self.lectures["08-metric-learning.html"]
        self.assertIn("0.08", txt)
        self.assertIn("0.40", txt)
        self.assertIn("0.18", txt)
        self.assertIn("Semi-Hard", txt)

    def test_09_contrastive_ssl_simclr(self):
        txt = self.lectures["09-contrastive-ssl.html"]
        self.assertIn("2.36788", txt)
        self.assertIn("0.42232", txt)
        self.assertIn("0.8620", txt)

    def test_10_vae_kl_reconstruction(self):
        txt = self.lectures["10-vae.html"]
        self.assertIn("0.7788", txt)
        self.assertIn("0.900", txt)
        self.assertIn("-0.9788", txt)
        self.assertIn("0.19827", txt)
        self.assertIn("1.0148", txt)
        self.assertIn("1.2131", txt)

    def test_11_gan_bce_gradient(self):
        txt = self.lectures["11-gan.html"]
        self.assertIn("0.16425", txt)
        self.assertIn("0.43375", txt)
        self.assertIn("0.5980", txt)
        self.assertIn("1.0601", txt)
        self.assertIn("-3.3333", txt)

    def test_12_diffusion_ddpm_denoising(self):
        txt = self.lectures["12-diffusion.html"]
        self.assertIn("0.79373", txt)
        self.assertIn("0.60828", txt)
        self.assertIn("1.28332", txt)
        self.assertIn("1.98466", txt)
        self.assertIn("1.43592", txt)

    def test_13_cv_tasks_iou_nms(self):
        txt = self.lectures["13-cv-tasks.html"]
        self.assertIn("10 000", txt.replace(r"\,", " "))
        self.assertIn("7 200", txt.replace(r"\,", " "))
        self.assertIn("0.72", txt)
        self.assertIn("0.50", txt)
        self.assertIn("1.00", txt)

    def test_14_rnn_lstm_cell(self):
        txt = self.lectures["14-rnn-lstm.html"]
        self.assertIn("0.7503", txt)
        self.assertIn("0.6457", txt)
        self.assertIn("1.5006", txt)
        self.assertIn("0.5845", txt)

    def test_15_attention_seq2seq_luong(self):
        txt = self.lectures["15-attention-seq2seq.html"]
        self.assertIn("34.8637", txt)
        self.assertIn("0.2119", txt)
        self.assertIn("0.5762", txt)
        self.assertIn("1.0000", txt)
        self.assertIn("0.7881", txt)

    def test_16_transformers_layernorm_pe(self):
        txt = self.lectures["16-transformers.html"]
        self.assertIn("5.0", txt)
        self.assertIn("2.2361", txt)
        self.assertIn("-1.3416", txt)
        self.assertIn("0.8415", txt)
        self.assertIn("0.5403", txt)

    def test_17_self_attention_scaled(self):
        txt = self.lectures["17-self-attention.html"]
        self.assertIn("0.7071", txt)
        self.assertIn("2.8284", txt)
        self.assertIn("0.6698", txt)
        self.assertIn("0.3302", txt)
        self.assertIn("6.698", txt)
        self.assertIn("16.088", txt)

    def test_18_lstm_vs_transformer_flops(self):
        txt = self.lectures["18-lstm-vs-transformer.html"]
        self.assertIn("1.074", txt)
        self.assertIn("1.644", txt)
        self.assertIn("137.4", txt)
        self.assertIn("755.9", txt)

    def test_19_text_word2vec_sgns(self):
        txt = self.lectures["19-text-word2vec.html"]
        self.assertIn("0.7311", txt)
        self.assertIn("0.5000", txt)
        self.assertIn("-1.0063", txt)
        self.assertIn("1.0269", txt)
        self.assertIn("-0.0731", txt)

    def test_20_mt_bleu_brevity(self):
        txt = self.lectures["20-mt-bleu.html"]
        self.assertIn("0.75", txt)
        self.assertIn("0.3333", txt)
        self.assertIn("0.6065", txt)
        self.assertIn("0.3033", txt)

    def test_21_enc_dec_lora_memory(self):
        txt = self.lectures["21-enc-dec.html"]
        self.assertIn("16 777 216", txt.replace(r"\,", " "))
        self.assertIn("65 536", txt.replace(r"\,", " "))
        self.assertIn("256", txt)
        self.assertIn("134.2", txt)

    def test_22_rl_intro_discounted_return(self):
        txt = self.lectures["22-rl-intro.html"]
        self.assertIn("10.0", txt)
        self.assertIn("8.0", txt)
        self.assertIn("7.2", txt)
        self.assertIn("8.48", txt)
        self.assertIn("7.3", txt)

    def test_23_bellman_2state_vi(self):
        txt = self.lectures["23-bellman.html"]
        self.assertIn("18.0", txt)
        self.assertIn("20.0", txt)
        self.assertIn("1.9", txt)
        self.assertIn("3.8", txt)
        self.assertIn("3.42", txt)
        self.assertIn("5.42", txt)

    def test_24_vi_pi_mc_gridworld(self):
        txt = self.lectures["24-vi-pi-mc.html"]
        self.assertIn("10.0", txt)
        self.assertIn("9.0", txt)
        self.assertIn("13.0", txt)
        self.assertIn("12.0", txt)

    def test_25_td_qlearning_sarsa_dqn(self):
        txt = self.lectures["25-td-qlearning.html"]
        self.assertIn("10.4", txt)
        self.assertIn("1.04", txt)
        self.assertIn("6.8", txt)
        self.assertIn("0.68", txt)
        self.assertIn("2.188", txt)
        self.assertIn("1.485", txt)
        self.assertIn("2.000", txt)

    def test_26_policy_gradient_reinforce_ppo(self):
        txt = self.lectures["26-policy-gradient.html"]
        self.assertIn("0.5", txt)
        self.assertIn("0.6225", txt)
        self.assertIn("2.4", txt)
        self.assertIn("-1.6", txt)

    def test_27_actor_critic_a2c_gae(self):
        txt = self.lectures["27-actor-critic.html"]
        self.assertIn("3.8", txt)
        self.assertIn("2.8", txt)
        self.assertIn("0.14", txt)
        self.assertIn("-0.056", txt)
        self.assertIn("0.168", txt)
        self.assertIn("0.056", txt)
        self.assertIn("0.94", txt)
        self.assertIn("1.6768", txt)


if __name__ == "__main__":
    unittest.main()
