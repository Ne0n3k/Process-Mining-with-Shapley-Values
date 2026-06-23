"""Driver for the main Shapley mining experiment on the three new event logs.

Runs MC (permutation) and RS (random-subset) estimators with convergence
diagnostics for three games (satisfiability, liveness, safety) across
3 logs x 4 noise thresholds. Persists per-config JSON, top-10 maps, and
CSV summaries under Docs/Problems/shapley_values/shapley.
"""
import warnings, time, json, os
warnings.filterwarnings("ignore")

from Functions.data_loading import (
    load_event_log, discover_tree_inductive, assign_tau_labels,
    LOG_PATHS, NOISE_LEVELS,
)
from Functions.tree_conversion import tree_to_named_pattern_expression
from Functions.logical_spec import WorkflowPatternTemplate
from Functions.utils.constants import PATTERN_RULES_PATH, OUT_SHAPLEY_DIR
from Functions.players import list_players_from_expression
from Functions.shapley import shapley_mc_convergence, shapley_rs_convergence
from Functions.ranking import kendall_tau_rank, jaccard_at_k, sort_players
from Functions.io import save_json, append_rows_csv

GAMES = ["satisfiability", "liveness", "safety"]
MC_STEPS = [50, 100, 200, 300, 500, 750, 1000]
RS_STEPS = [100, 200, 400, 800, 1200, 1600, 2000]

MAPS_DIR = os.path.join(OUT_SHAPLEY_DIR, "maps")
STAB_DIR = os.path.join(OUT_SHAPLEY_DIR, "stability")
PLAYERS_CSV = os.path.join(OUT_SHAPLEY_DIR, "players_values.csv")
CONFIGS_CSV = os.path.join(OUT_SHAPLEY_DIR, "configs_meta.csv")
STAB_CSV = os.path.join(OUT_SHAPLEY_DIR, "stability_summary.csv")


def build_named(log_obj, noise):
    tree = discover_tree_inductive(log_obj, noise=noise)
    tree = assign_tau_labels(tree)
    return tree_to_named_pattern_expression(tree)


def main():
    print("== Loading templates and logs ==", flush=True)
    TEMPLATES = WorkflowPatternTemplate.load_pattern_property_set(PATTERN_RULES_PATH)
    EVENT_LOGS = {name: load_event_log(path) for name, path in LOG_PATHS.items()}
    for name in EVENT_LOGS:
        print(f"  {name}: events={len(EVENT_LOGS[name])}", flush=True)

    # Build named expressions and player counts, then order configs small->large.
    configs = []
    for log_name, log_obj in EVENT_LOGS.items():
        for noise in NOISE_LEVELS:
            named = build_named(log_obj, noise)
            players = list_players_from_expression(named)
            configs.append({
                "log": log_name, "noise": noise, "named": named,
                "n_players": len(players),
            })
    configs.sort(key=lambda c: c["n_players"])

    grand_t0 = time.time()
    total = len(configs) * len(GAMES)
    done = 0
    for c in configs:
        log_name, noise, named = c["log"], c["noise"], c["named"]
        for game in GAMES:
            done += 1
            out_json = os.path.join(OUT_SHAPLEY_DIR, log_name, str(noise), f"{game}.json")
            if os.path.exists(out_json):
                print(f"[{done}/{total}] SKIP (exists) {log_name} noise={noise} {game}", flush=True)
                continue
            print(f"[{done}/{total}] RUN {log_name} noise={noise} {game} "
                  f"players={c['n_players']} (elapsed {time.time()-grand_t0:.0f}s)", flush=True)

            mc = shapley_mc_convergence(named, TEMPLATES, game, steps=MC_STEPS,
                                        seed=42, progress_every=200)
            rs = shapley_rs_convergence(named, TEMPLATES, game, steps=RS_STEPS,
                                        seed=123, progress_every=400)

            mc_vals = mc["snapshots"][-1]
            rs_vals = rs["snapshots"][-1]
            ktau = kendall_tau_rank(mc_vals, rs_vals)
            jac = jaccard_at_k(mc_vals, rs_vals, k=10)

            ordered = sort_players(mc_vals)
            slices = {p.id: p.snippet for p in list_players_from_expression(named)}

            # Per-config JSON
            save_json(out_json, {
                "log": log_name, "noise": noise, "game": game,
                "n_players": c["n_players"],
                "mc_values": mc_vals, "rs_values": rs_vals,
                "mc_steps": MC_STEPS, "rs_steps": RS_STEPS,
                "mc_deltas_max": mc["deltas_max"], "mc_deltas_l1": mc["deltas_l1"],
                "rs_deltas_max": rs["deltas_max"], "rs_deltas_l1": rs["deltas_l1"],
                "mc_duration": mc["duration"], "rs_duration": rs["duration"],
                "mc_cache_entries": mc["cache_entries"],
                "kendall_tau_mc_rs": ktau, "jaccard10_mc_rs": jac,
            })

            # Top-10 text map
            map_path = os.path.join(MAPS_DIR, log_name, str(noise), f"{game}_top10.txt")
            os.makedirs(os.path.dirname(map_path), exist_ok=True)
            with open(map_path, "w", encoding="utf-8") as f:
                f.write(f"# {log_name} noise={noise} game={game} (MC, n_perm=1000)\n")
                for rank, pid in enumerate(ordered[:10], 1):
                    f.write(f"{rank:>2}. {pid:<24} {mc_vals[pid]:+.4f}  {slices.get(pid,'')}\n")

            # CSV rows: player values
            append_rows_csv(PLAYERS_CSV, [
                {"log": log_name, "noise": noise, "game": game, "player": pid,
                 "mc_value": round(mc_vals[pid], 6),
                 "rs_value": round(rs_vals.get(pid, 0.0), 6)}
                for pid in ordered
            ])

            # CSV row: config meta
            append_rows_csv(CONFIGS_CSV, [{
                "log": log_name, "noise": noise, "game": game,
                "n_players": c["n_players"],
                "mc_seconds": round(mc["duration"], 2),
                "rs_seconds": round(rs["duration"], 2),
                "mc_cache_entries": mc["cache_entries"],
            }])

            # CSV + JSON: stability summary
            stab = {
                "log": log_name, "noise": noise, "game": game,
                "kendall_tau_mc_rs": round(ktau, 4),
                "jaccard10_mc_rs": round(jac, 4),
                "mc_final_delta_max": round(mc["deltas_max"][-1], 6),
                "mc_final_delta_l1": round(mc["deltas_l1"][-1], 6),
                "rs_final_delta_max": round(rs["deltas_max"][-1], 6),
                "rs_final_delta_l1": round(rs["deltas_l1"][-1], 6),
            }
            append_rows_csv(STAB_CSV, [stab])
            save_json(os.path.join(STAB_DIR, f"{log_name}__{noise}__{game}.json"), {
                "log": log_name, "noise": noise, "game": game,
                "mc_steps": MC_STEPS, "mc_deltas_max": mc["deltas_max"], "mc_deltas_l1": mc["deltas_l1"],
                "rs_steps": RS_STEPS, "rs_deltas_max": rs["deltas_max"], "rs_deltas_l1": rs["deltas_l1"],
                "kendall_tau_mc_rs": ktau, "jaccard10_mc_rs": jac,
            })

            print(f"        done: mc={mc['duration']:.0f}s rs={rs['duration']:.0f}s "
                  f"tau={ktau:.3f} jac@10={jac:.3f}", flush=True)

    print(f"== ALL DONE in {time.time()-grand_t0:.0f}s ==", flush=True)


if __name__ == "__main__":
    main()
