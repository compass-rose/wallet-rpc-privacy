#!/usr/bin/env python3
"""完整测试脚本 - 使用现有Session并保存结果到文件夹"""

import requests
import json
import os
from datetime import datetime
from pathlib import Path

API_BASE = "http://localhost:8000/api/v1"
OUTPUT_DIR = "test_results"

# 创建输出目录
def ensure_output_dir():
    """确保输出目录存在"""
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    print(f"✓ 输出目录: {os.path.abspath(OUTPUT_DIR)}")

# 获取现有session and the traffic data for each
def get_existing_sessions_with_traffic():
    """获取数据库中的所有session及其流量数据"""
    response = requests.get(f"{API_BASE}/sessions")
    data = response.json()
    
    if data["success"]:
        # API返回的数据结构是 { data: { sessions: [...] } }
        sessions = data["data"]["sessions"]
        print(f"找到 {len(sessions)} 个session")
        print(f"{'ID':<12} {'状态':<10} {'包数量':<10} {'钱包类型'}")
        
        # 获取每个session的流量数据
        sessions_with_traffic = []
        for session in sessions:
            traffic_response = requests.get(f"{API_BASE}/sessions/{session['id']}/traffic")
            traffic_data = traffic_response.json()
            
            if traffic_data["success"]:
                traffic_count = traffic_data["data"].get("total", 0)
                session["traffic_count"] = traffic_count
            else:
                session["traffic_count"] = 0
            
            print(f"{session['id'][:12]:12} {session['status']:<10} {session['traffic_count']:<10} {session['wallet_type']}")
            
            sessions_with_traffic.append(session)
        
        return sessions_with_traffic
    else:
        print("✗ 获取session失败")
        return []

# 运行基础评估
def run_assessment(session_id):
    """运行基础风险评估并保存结果"""
    response = requests.post(f"{API_BASE}/sessions/{session_id}/assess")
    
    if response.status_code == 200:
        data = response.json()['data']
        # 保存到文件
        filename = f"{OUTPUT_DIR}/assessment_{session_id[:12]}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ 评估结果已保存: {filename}")
        return data
    else:
        print(f"✗ 评估失败: {response.json()}")
        return None

# 运行基线对比
def run_baseline_comparison(session_id):
    """运行基线对比并保存结果"""
    response = requests.post(f"{API_BASE}/sessions/{session_id}/baseline-compare")
    
    if response.status_code == 200:
        data = response.json()['data']
        # 保存到文件
        filename = f"{OUTPUT_DIR}/baseline_comparison_{session_id[:12]}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # 同时保存为可读的文本格式
        txt_filename = f"{OUTPUT_DIR}/baseline_comparison_{session_id[:12]}.txt"
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("基线对比报告\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Session ID: {session_id}\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            baseline = data['baseline_comparison']
            f.write(f"【总体隐私评分】\n")
            f.write(f"  评分: {baseline['overall_privacy_score']}/100\n")
            f.write(f"  等级: {baseline['privacy_level']}\n\n")
            
            f.write(f"【指标对比】\n")
            for metric in ['entropy', 'uniqueness', 'correlation', 'temporal']:
                actual = baseline['actual'][metric]
                random = baseline['random_baseline'][metric]
                ideal = baseline['ideal_baseline'][metric]
                vs_random = baseline['comparison'][metric]['vs_random']
                vs_ideal = baseline['comparison'][metric]['vs_ideal']
                
                f.write(f"  {metric}:\n")
                f.write(f"    实际值: {actual:.3f}\n")
                f.write(f"    随机基线: {random:.3f} ({vs_random})\n")
                f.write(f"    理想基线: {ideal:.3f} ({vs_ideal})\n")
            
            industry = data['industry_comparison']
            f.write(f"\n【行业对比】\n")
            f.write(f"  平均百分位: {industry['overall_industry_ranking']['average_percentile']}%\n")
            f.write(f"  排名水平: {industry['overall_industry_ranking']['ranking_text']}\n")
        
        print(f"✓ 基线对比已保存: {filename}")
        print(f"✓ 文本报告已保存: {txt_filename}")
        return data
    else:
        print(f"✗ 基线对比失败: {response.json()}")
        return None

# 运行模拟攻击
def run_simulate_attack(session_id):
    """运行模拟攻击并保存结果"""
    response = requests.post(f"{API_BASE}/sessions/{session_id}/simulate-attack")
    
    if response.status_code == 200:
        data = response.json()['data']
        # 保存到文件
        filename = f"{OUTPUT_DIR}/simulate_attack_{session_id[:12]}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # 保存为可读的文本格式
        txt_filename = f"{OUTPUT_DIR}/simulate_attack_{session_id[:12]}.txt"
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("模拟攻击报告\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Session ID: {session_id}\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"攻击类型: {data['attack_type']}\n")
            f.write(f"使用Session数: {data['num_sessions']}\n\n")
            
            overall = data['overall_attack_effectiveness']
            f.write(f"【总体攻击有效性】\n")
            f.write(f"  有效性分数: {overall['value']:.3f}\n")
            f.write(f"  攻击成功率: {overall['percentage']:.1f}%\n")
            f.write(f"  风险等级: {overall['risk_level']}\n\n")
            
            f.write(f"【分类器结果】\n")
            for model_name, model_result in data['classifiers'].items():
                f.write(f"  {model_name}:\n")
                f.write(f"    训练准确率: {model_result['train_accuracy']:.2%}\n")
                test_acc = model_result.get('test_accuracy', 0)
                if isinstance(test_acc, dict):
                    test_acc = 0
                attack_rate = model_result.get('attack_success_rate', 0)
                if isinstance(attack_rate, dict):
                    attack_rate = 0
                precision = model_result.get('precision', 0)
                if isinstance(precision, dict):
                    precision = 0
                recall = model_result.get('recall', 0)
                if isinstance(recall, dict):
                    recall = 0
                f1 = model_result.get('f1_score', 0)
                if isinstance(f1, dict):
                    f1 = 0
                f.write(f"    测试准确率: {test_acc:.2%}\n")
                f.write(f"    攻击成功率: {attack_rate:.2%}\n")
                f.write(f"    精确率: {precision:.2%}\n")
                f.write(f"    召回率: {recall:.2%}\n")
                f.write(f"    F1分数: {f1:.2%}\n\n")

            clustering = data.get('clustering', {})
            f.write(f"【聚类攻击】\n")
            silhouette = clustering.get('silhouette_score') or 0
            if isinstance(silhouette, dict):
                silhouette = 0
            purity = clustering.get('cluster_purity') or 0
            if isinstance(purity, dict):
                purity = 0
            f.write(f"  聚类数量: {clustering.get('n_clusters', 0)}\n")
            f.write(f"  轮廓系数: {silhouette:.3f}\n")
            f.write(f"  聚类纯度: {purity:.3f}\n")
        
        print(f"✓ 模拟攻击结果已保存: {filename}")
        print(f"✓ 文本报告已保存: {txt_filename}")
        return data
    else:
        error = response.json()
        print(f"✗ 模拟攻击失败: {error.get('error', error)}")
        return None

# 运行对抗性测试
def run_adversarial_test(session_id):
    """运行对抗性测试并保存结果"""
    response = requests.post(f"{API_BASE}/sessions/{session_id}/adversarial-test")
    
    if response.status_code == 200:
        data = response.json()['data']
        # 保存到文件
        filename = f"{OUTPUT_DIR}/adversarial_test_{session_id[:12]}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # 保存为可读的文本格式
        txt_filename = f"{OUTPUT_DIR}/adversarial_test_{session_id[:12]}.txt"
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("对抗性测试报告\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Session ID: {session_id}\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"测试Session数: {data['num_sessions']}\n\n")
            
            baseline_effect = data.get('baseline', {}).get('overall_attack_effectiveness', 0)
            if isinstance(baseline_effect, dict):
                baseline_effect = 0
            f.write(f"【基线攻击有效性】: {baseline_effect:.3f}\n\n")
            
            f.write(f"【防御策略效果】\n")
            for strategy, result in data['defense_strategies'].items():
                f.write(f"  {strategy}:\n")
                ae_after = result.get('attack_effectiveness_after', 0)
                if isinstance(ae_after, dict):
                    ae_after = 0
                reduction = result.get('effectiveness_reduction', 0)
                if isinstance(reduction, dict):
                    reduction = 0
                risk_reduction = result.get('reduction_percentage', 0)
                if isinstance(risk_reduction, dict):
                    risk_reduction = 0
                f.write(f"    应用后攻击有效性: {ae_after:.3f}\n")
                f.write(f"    有效性降低: {reduction:.3f}\n")
                f.write(f"    风险降低: {risk_reduction:.2f}%\n")
                f.write(f"    效果评级: {result['effectiveness_rating']}\n\n")
            
            best = data['best_strategy']
            f.write(f"【最佳策略】\n")
            f.write(f"  策略: {best['name']}\n")
            f.write(f"  预期风险降低: {best['expected_risk_reduction_percent']:.2f}%\n\n")
            
            f.write(f"【推荐措施】\n")
            for rec in data['recommendations']:
                if rec.get('type') == 'high_level':
                    f.write(f"  ⚠ {rec['message']} (优先级: {rec['priority']})\n")
                else:
                    f.write(f"  ✓ 策略: {rec['strategy']}\n")
                    f.write(f"    风险降低: {rec['risk_reduction_percent']:.2f}%\n")
                    f.write(f"    状态: {rec['status']}\n")
                    f.write(f"    效果: {rec['effectiveness']}\n")
            
            improvement = data.get('overall_improvement', {})
            if improvement:
                f.write(f"\n【总体改进】\n")
                f.write(f"  基线有效性: {improvement['baseline_effectiveness']:.3f}\n")
                f.write(f"  最佳防御后: {improvement['best_defended_effectiveness']:.3f}\n")
                f.write(f"  总体风险降低: {improvement['overall_risk_reduction_percent']:.2f}%\n")
        
        print(f"✓ 对抗性测试已保存: {filename}")
        print(f"✓ 文本报告已保存: {txt_filename}")
        return data
    else:
        error = response.json()
        print(f"✗ 对抗性测试失败: {error.get('error', error)}")
        return None

# 生成综合报告
def generate_summary_report(results, sessions, timestamp):
    """生成综合测试报告"""
    report_file = os.path.join(OUTPUT_DIR, f"summary_report_{timestamp}.txt")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("钱包RPC隐私泄露测量系统 - 完整测试报告\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"测试Session数: {len(sessions)}\n\n")
        
        # Session列表
        f.write("=" * 80 + "\n")
        f.write("测试Session列表\n")
        f.write("=" * 80 + "\n")
        for i, session in enumerate(sessions, 1):
            f.write(f"{i}. ID: {session['id']}\n")
            f.write(f"   钱包类型: {session['wallet_type']}\n")
            f.write(f"   RPC提供商: {session['rpc_provider']}\n")
            f.write(f"   状态: {session['status']}\n\n")
        
        # 基础评估总结
        f.write("=" * 80 + "\n")
        f.write("基础评估总结\n")
        f.write("=" * 80 + "\n")
        for i, session in enumerate(sessions, 1):
            session_id = session['id']
            assessment = results.get(f"assessment_{session_id}")
            if assessment:
                f.write(f"{i}. {session_id}:\n")
                f.write(f"   整体评分: {assessment['overall_score']}/100\n")
                f.write(f"   风险等级: {assessment['risk_level']}\n")
                f.write(f"   信息熵: {assessment['entropy_score']:.3f}\n")
                f.write(f"   唯一性: {assessment['uniqueness_score']:.3f}\n")
                f.write(f"   关联性: {assessment['correlation_score']:.3f}\n")
                f.write(f"   时效性: {assessment['temporal_score']:.3f}\n\n")
        
        # 基线对比总结
        if 'baseline' in results and results['baseline']:
            baseline = results['baseline']['baseline_comparison']
            industry = results['baseline']['industry_comparison']
            
            f.write("=" * 80 + "\n")
            f.write("基线对比总结\n")
            f.write("=" * 80 + "\n")
            f.write(f"总体隐私评分: {baseline['overall_privacy_score']}/100\n")
            f.write(f"隐私等级: {baseline['privacy_level']}\n\n")
            
            f.write("指标详情:\n")
            for metric in ['entropy', 'uniqueness', 'correlation', 'temporal']:
                actual = baseline['actual'][metric]
                random = baseline['random_baseline'][metric]
                ideal = baseline['ideal_baseline'][metric]
                vs_random = baseline['comparison'][metric]['vs_random']
                vs_ideal = baseline['comparison'][metric]['vs_ideal']
                
                f.write(f"  {metric:12} | 实际: {actual:.3f} | 随机: {random:.3f} ({vs_random:10}) | 理想: {ideal:.3f} ({vs_ideal:10})\n")
            
            f.write(f"\n行业对比:\n")
            f.write(f"  平均百分位: {industry['overall_industry_ranking']['average_percentile']}%\n")
            f.write(f"  排名水平: {industry['overall_industry_ranking']['ranking_text']}\n\n")
            
            f.write("百分位排名:\n")
            for metric, ranking in industry['percentile_rankings'].items():
                f.write(f"  {metric:12} | 第 {ranking['percentile']:3} 百分位\n")
        
        # 模拟攻击总结
        if 'attack' in results and results['attack']:
            attack = results['attack']
            overall = attack.get('overall_attack_effectiveness', 0)
            if isinstance(overall, dict):
                overall = 0

            f.write("=" * 80 + "\n")
            f.write("模拟攻击总结\n")
            f.write("=" * 80 + "\n")
            f.write(f"攻击类型: {attack['attack_type']}\n")
            f.write(f"使用Session数: {attack['num_sessions']}\n\n")

            f.write("分类器结果:\n")
            for model_name, model_result in attack['classifiers'].items():
                f.write(f"  {model_name}:\n")
                train_acc = model_result.get('train_accuracy', 0)
                if isinstance(train_acc, dict):
                    train_acc = 0
                test_acc = model_result.get('test_accuracy', 0)
                if isinstance(test_acc, dict):
                    test_acc = 0
                attack_rate = model_result.get('attack_success_rate', 0)
                if isinstance(attack_rate, dict):
                    attack_rate = 0
                f1 = model_result.get('f1_score', 0)
                if isinstance(f1, dict):
                    f1 = 0
                f.write(f"    训练准确率: {train_acc:.2%}\n")
                f.write(f"    测试准确率: {test_acc:.2%}\n")
                f.write(f"    攻击成功率: {attack_rate:.2%}\n")
                f.write(f"    F1分数: {f1:.2%}\n\n")

            clustering = attack.get('clustering', {})
            f.write("聚类攻击:\n")
            f.write(f"  聚类数量: {clustering.get('n_clusters', 0)}\n")
            silhouette = clustering.get('silhouette_score', 0)
            if isinstance(silhouette, dict):
                silhouette = 0
            f.write(f"  轮廓系数: {silhouette:.3f}\n")
            purity = clustering.get('cluster_purity', 0)
            if isinstance(purity, dict):
                purity = 0
            f.write(f"  聚类纯度: {purity:.3f}\n\n")

            f.write("总体攻击有效性:\n")
            overall_value = overall.get('value', 0) if isinstance(overall, dict) else overall
            if isinstance(overall_value, dict):
                overall_value = 0
            f.write(f"  有效性分数: {overall_value:.3f}\n")
            overall_percentage = overall.get('percentage', 0) if isinstance(overall, dict) else 0
            if isinstance(overall_percentage, dict):
                overall_percentage = 0
            f.write(f"  攻击成功率: {overall_percentage:.1f}%\n")
            overall_risk = overall.get('risk_level', '未知') if isinstance(overall, dict) else '未知'
            f.write(f"  风险等级: {overall_risk}\n")

            # 风险评估
            if overall_percentage >= 80:
                risk = "严重 - 攻击者极易区分用户"
            elif overall_percentage >= 60:
                risk = "高 - 攻击者较容易区分用户"
            elif overall_percentage >= 40:
                risk = "中 - 攻击者有一定区分能力"
            else:
                risk = "低 - 攻击者难以区分用户"
            f.write(f"  风险评估: {risk}\n")
        
        # 对抗性测试总结
        if 'adversarial' in results and results['adversarial']:
            adversarial = results['adversarial']
            best = adversarial['best_strategy']
            improvement = adversarial.get('overall_improvement', {})

            f.write("\n" + "=" * 80 + "\n")
            f.write("对抗性测试总结\n")
            f.write("=" * 80 + "\n")
            baseline_effect = adversarial.get('baseline', {}).get('overall_attack_effectiveness', 0)
            if isinstance(baseline_effect, dict):
                baseline_effect = 0
            f.write(f"基线攻击有效性: {baseline_effect:.3f}\n\n")

            f.write("防御策略效果:\n")
            for strategy, result in adversarial['defense_strategies'].items():
                f.write(f"  {strategy}:\n")
                reduction = result.get('reduction_percentage', 0)
                if isinstance(reduction, dict):
                    reduction = 0
                f.write(f"    风险降低: {reduction:.2f}%\n")
                f.write(f"    效果评级: {result['effectiveness_rating']}\n\n")

            f.write("推荐措施:\n")
            for rec in adversarial['recommendations']:
                if rec.get('type') == 'high_level':
                    f.write(f"  ⚠ {rec['message']} (优先级: {rec['priority']})\n")
                else:
                    f.write(f"  ✓ {rec['strategy']}: {rec['status']} ({rec['effectiveness']})\n")

            f.write(f"\n最佳策略: {best['name']}\n")
            expected_reduction = best.get('expected_risk_reduction_percent', 0)
            if isinstance(expected_reduction, dict):
                expected_reduction = 0
            f.write(f"预期风险降低: {expected_reduction:.2f}%\n")

            if improvement:
                f.write(f"\n总体改进:\n")
                baseline_eff = improvement.get('baseline_effectiveness', 0)
                if isinstance(baseline_eff, dict):
                    baseline_eff = 0
                f.write(f"  基线有效性: {baseline_eff:.3f}\n")
                best_defended = improvement.get('best_defended_effectiveness', 0)
                if isinstance(best_defended, dict):
                    best_defended = 0
                f.write(f"  最佳防御后: {best_defended:.3f}\n")
                overall_reduction = improvement.get('overall_risk_reduction_percent', 0)
                if isinstance(overall_reduction, dict):
                    overall_reduction = 0
                f.write(f"  总体风险降低: {overall_reduction:.2f}%\n")
        
        # 最终总结
        f.write("\n" + "=" * 80 + "\n")
        f.write("最终总结\n")
        f.write("=" * 80 + "\n")
        
        if 'baseline' in results and results['baseline']:
            privacy_score = results['baseline']['baseline_comparison']['overall_privacy_score']
            f.write(f"隐私保护水平: {privacy_score}/100\n")
        
        if 'attack' in results and results['attack']:
            attack_success = results['attack']['overall_attack_effectiveness']['percentage']
            f.write(f"攻击风险: {attack_success:.1f}%\n")
        
        if 'adversarial' in results and results['adversarial']:
            best_strategy = results['adversarial']['best_strategy']['name']
            risk_reduction = results['adversarial']['best_strategy']['expected_risk_reduction_percent']
            f.write(f"推荐防御策略: {best_strategy}\n")
            f.write(f"预期风险降低: {risk_reduction:.2f}%\n")
        
        f.write("\n所有测试结果文件已保存在: " + os.path.abspath(OUTPUT_DIR) + "\n")
    
    print(f"✓ 综合报告已保存: {report_file}")

# 主流程
def main():
    """主测试流程"""
    
    # 确保输出目录存在
    ensure_output_dir()
    
    # 生成时间戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 获取现有session和流量数据
    print("\n" + "=" * 80)
    print("1. 获取现有Session及流量数据")
    print("=" * 80)
    
    sessions = get_existing_sessions_with_traffic()
    
    if len(sessions) < 2:
        print(f"\n✗ 错误: 需要至少2个session进行测试")
        print(f"  当前只有 {len(sessions)} 个session")
        return
    
    # 筛选有流量数据的session（至少5条流量记录）
    sessions_with_traffic = [s for s in sessions if s.get('traffic_count', 0) >= 5]
    
    if len(sessions_with_traffic) < 1:
        print(f"\n⚠ 警告: 没有足够的流量数据进行测试")
        print(f"  至少需要5条流量记录来运行模拟攻击和对抗性测试")
        print(f"  当前session流量数据:")
        for session in sessions:
            print(f"    {session['id']}: {session.get('traffic_count', 0)} 条")
        print(f"\n请运行流量捕获后再重试:")
        print(f"  curl -X POST \"{API_BASE}/sessions/{{session_id}}/traffic/start\"")
        return
    
    test_sessions = sessions_with_traffic[:3]
    print(f"\n使用 {len(test_sessions)} 个有流量数据的session进行测试")
    
    results = {}
    
    # 2. 基础评估
    print("\n" + "=" * 80)
    print("2. 基础评估")
    print("=" * 80)
    
    for session in test_sessions:
        print(f"\nSession: {session['id']}")
        assessment = run_assessment(session['id'])
        results[f"assessment_{session['id']}"] = assessment
    
    # 3. 基线对比
    print("\n" + "=" * 80)
    print("3. 基线对比")
    print("=" * 80)
    print(f"Session: {test_sessions[0]['id']}")
    
    baseline_result = run_baseline_comparison(test_sessions[0]['id'])
    results['baseline'] = baseline_result
    
    # 4. 模拟攻击
    print("\n" + "=" * 80)
    print("4. 模拟攻击")
    print("=" * 80)
    print(f"Session: {test_sessions[0]['id']}")
    
    attack_result = run_simulate_attack(test_sessions[0]['id'])
    results['attack'] = attack_result
    
    # 5. 对抗性测试
    print("\n" + "=" * 80)
    print("5. 对抗性测试")
    print("=" * 80)
    print(f"Session: {test_sessions[0]['id']}")
    
    adversarial_result = run_adversarial_test(test_sessions[0]['id'])
    results['adversarial'] = adversarial_result
    
    # 6. 生成综合报告
    print("\n" + "=" * 80)
    print("6. 生成综合报告")
    print("=" * 80)
    
    generate_summary_report(results, test_sessions, timestamp)
    
    # 保存完整JSON结果
    complete_json = os.path.join(OUTPUT_DIR, f"complete_results_{timestamp}.json")
    with open(complete_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"✓ 完整JSON结果已保存: {complete_json}")
    
    # 完成
    print("\n" + "=" * 80)
    print("测试完成! 所有结果已保存到:", os.path.abspath(OUTPUT_DIR))
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    except Exception as e:
        print(f"\n\n错误: {e}")
        import traceback
        traceback.print_exc()
