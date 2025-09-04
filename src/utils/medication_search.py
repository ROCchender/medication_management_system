from typing import Dict, Any, List, Optional
import requests
import logging
import json

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 模拟药物数据库（实际应用中可以从外部API获取）
MOCK_MEDICATION_DATABASE = {
    "布洛芬": {
        "功效": "用于缓解轻至中度疼痛如头痛、关节痛、偏头痛、牙痛、肌肉痛、神经痛、痛经。也用于普通感冒或流行性感冒引起的发热。",
        "用法": "口服。成人一次0.4-0.6g，一日3-4次，饭后服用。",
        "图片": "https://example.com/images/ibuprofen.jpg",
        "副作用": "恶心、呕吐、胃灼热感或轻度消化不良、胃肠道溃疡及出血、转氨酶升高、头痛、头晕、耳鸣、视力模糊、精神紧张、嗜睡、下肢水肿或体重骤增。",
        "注意事项": "对其他非甾体抗炎药过敏者禁用；孕妇及哺乳期妇女禁用；对阿司匹林过敏的哮喘患者禁用；严重肝肾功能不全者或严重心力衰竭者禁用；正在服用其他含有布洛芬或其他非甾体抗炎药的患者禁用。"
    },
    "阿司匹林": {
        "功效": "用于普通感冒或流行性感冒引起的发热，也用于缓解轻至中度疼痛如头痛、关节痛、偏头痛、牙痛、肌肉痛、神经痛、痛经。",
        "用法": "口服。成人一次0.3-0.6g，一日3次，饭后服用。",
        "图片": "https://example.com/images/aspirin.jpg",
        "副作用": "恶心、呕吐、上腹部不适或疼痛等胃肠道反应，停药后多可消失；长期或大量应用时可发生胃肠道出血或溃疡；在服用一定疗程后可出现可逆性耳鸣、听力下降；少数病人可发生哮喘、荨麻疹、血管神经性水肿或休克等过敏反应，严重者可致死亡；剂量过大时可致肝肾功能损害。",
        "注意事项": "对本品过敏者禁用；血友病或血小板减少症患者禁用；活动性溃疡病或其他原因引起的消化道出血患者禁用；有阿司匹林或其他非甾体抗炎药过敏史者，尤其是出现哮喘、神经血管性水肿或休克者禁用。"
    },
    "对乙酰氨基酚": {
        "功效": "用于普通感冒或流行性感冒引起的发热，也用于缓解轻至中度疼痛如头痛、关节痛、偏头痛、牙痛、肌肉痛、神经痛、痛经。",
        "用法": "口服。成人一次0.3-0.6g，若持续发热或疼痛，可间隔4-6小时重复用药一次，24小时内不超过4次。",
        "图片": "https://example.com/images/paracetamol.jpg",
        "副作用": "偶见皮疹、荨麻疹、药热及粒细胞减少。长期大量用药会导致肝肾功能异常。",
        "注意事项": "严重肝肾功能不全者禁用；对本品过敏者禁用；对阿司匹林过敏者慎用；不能同时服用其他含有解热镇痛药的药品（如某些复方抗感冒药）；服用本品期间不得饮酒或含有酒精的饮料。"
    },
    "头孢拉定": {
        "功效": "适用于敏感菌所致的急性咽炎、扁桃体炎、中耳炎、支气管炎和肺炎等呼吸道感染、泌尿生殖道感染及皮肤软组织感染等。",
        "用法": "口服。成人一次0.25-0.5g，每6小时一次，一日最高剂量为4g。",
        "图片": "https://example.com/images/cephradine.jpg",
        "副作用": "恶心、呕吐、腹泻、上腹部不适等胃肠道反应较为常见；药疹发生率约1%-3%；伪膜性肠炎、嗜酸粒细胞增多、直接Coombs试验阳性反应、周围血象白细胞及中性粒细胞减少、头晕、胸闷、念珠菌阴道炎及过敏反应等见于个别患者。",
        "注意事项": "对头孢菌素过敏者及有青霉素过敏性休克或即刻反应史者禁用；在应用本品前须详细询问患者对头孢菌素类、青霉素类及其他药物过敏史；本品主要经肾排出，肾功能减退者须减少剂量或延长给药间期；应用本品的患者以硫酸铜法测定尿糖时可出现假阳性反应。"
    },
    "阿莫西林": {
        "功效": "用于敏感菌（不产β内酰胺酶菌株）所致的下列感染：中耳炎、鼻窦炎、咽炎、扁桃体炎等上呼吸道感染；泌尿生殖道感染；皮肤软组织感染；急性支气管炎、肺炎等下呼吸道感染；急性单纯性淋病。",
        "用法": "口服。成人一次0.5g，每6-8小时一次，一日剂量不超过4g。",
        "图片": "https://example.com/images/amoxicillin.jpg",
        "副作用": "恶心、呕吐、腹泻及假膜性肠炎等胃肠道反应；皮疹、药物热和哮喘等过敏反应；贫血、血小板减少、嗜酸性粒细胞增多等；血清氨基转移酶可轻度增高；由念珠菌或耐药菌引起的二重感染；偶见兴奋、焦虑、失眠、头晕以及行为异常等中枢神经系统症状。",
        "注意事项": "青霉素类药物偶可致过敏性休克，用药前必须详细询问药物过敏史并作青霉素皮肤试验；传染性单核细胞增多症患者应用本品易发生皮疹，应避免使用；疗程较长患者应检查肝、肾功能和血常规；阿莫西林可导致采用Benedict或Fehling试剂的尿糖试验出现假阳性；下列情况应慎用：有哮喘、枯草热等过敏性疾病史者；老年人和肾功能严重损害时可能须调整剂量。"
    },
    "盐酸左西替利嗪": {
        "功效": "用于缓解变态反应性疾病的过敏症状，如：变应性鼻炎（包括眼睛的过敏症状）、荨麻疹、血管神经性水肿、接触性皮炎、虫咬性皮炎等皮肤粘膜的过敏性疾病；用于减轻感冒时的过敏症状。",
        "用法": "口服。成人及6岁以上儿童：每日一次，每次5mg，空腹或餐中或餐后均可服用。",
        "图片": "https://example.com/images/levocetirizine.jpg",
        "副作用": "常见不良反应有嗜睡、口干、头痛、乏力等，均为轻度。",
        "注意事项": "有肝功能障碍或障碍史者慎用；高空作业、驾驶或操作机器期间慎用；避免与镇静剂同服；酒后避免使用本品；肾功能减损患者使用本品适当减量；妊期及哺乳期妇女禁用本品；2周岁以下儿童用药的安全性尚未确定；通常老年人生理机能衰退，需慎用本品。"
    },
    "盐酸氨溴索": {
        "功效": "适用于伴有痰液粘稠、排痰困难的急性、慢性呼吸系统疾病，如慢性支气管炎急性加重、喘息型支气管炎、支气管扩张及支气管哮喘的祛痰治疗。",
        "用法": "口服。成人，一次30mg，一日3次，长期服用者可减为一日2次。",
        "图片": "https://example.com/images/ambroxol.jpg",
        "副作用": "偶见皮疹、恶心、胃部不适、食欲缺乏、腹痛、腹泻。",
        "注意事项": "孕妇及哺乳期妇女慎用；应避免与中枢性镇咳药（如右美沙芬等）同时使用，以免稀化的痰液堵塞气道；本品为一种粘液调节剂，仅对咳痰症状有一定作用，在使用时应注意咳嗽、咳痰的原因，如使用7日后未见好转，应及时就医。"
    },
    "盐酸二甲双胍": {
        "功效": "用于单纯饮食控制不满意的Ⅱ型糖尿病病人，尤其是肥胖和伴高胰岛素血症者，用本药不但有降血糖作用，还可能有减轻体重和高胰岛素血症的效果。对某些磺酰脲类疗效差的患者可奏效，如与磺酰脲类、小肠糖苷酶抑制剂或噻唑烷二酮类降糖药合用，较分别单用的效果更好。亦可用于胰岛素治疗的患者，以减少胰岛素用量。",
        "用法": "口服。成人开始一次0.25g，一日2-3次，以后根据疗效逐渐加量，一般每日量1-1.5g，最多每日不超过2g。餐中或餐后即刻服用，可减轻胃肠道反应。",
        "图片": "https://example.com/images/metformin.jpg",
        "副作用": "常见的有：恶心、呕吐、腹泻、口中有金属味；有时有乏力、疲倦、头晕、皮疹；乳酸性酸中毒虽然发生率很低，但应予注意；可减少肠道吸收维生素B12，使血红蛋白减少，产生巨红细胞贫血，也可引起吸收不良。",
        "注意事项": "Ⅱ型糖尿病伴有酮症酸中毒、肝及肾功能不全（血清肌酐超过1.5mg/dl）、肺功能不全、心力衰竭、急性心肌梗死、严重感染和外伤、重大手术以及临床有低血压和缺氧情况；糖尿病合并严重的慢性并发症（如糖尿病肾病、糖尿病眼底病变）；静脉肾盂造影或动脉造影前；酗酒者；严重心、肺疾病患者；维生素B12、叶酸和铁缺乏的患者；全身情况较差的患者（如营养不良、脱水）禁用。"
    },
    "硝苯地平": {
        "功效": "用于高血压（单独或与其他降压药合用）；心绞痛：尤其是变异型心绞痛。",
        "用法": "口服。成人常用量：开始一次10mg，一日3次；常用的维持剂量为口服10-20mg，一日3次。部分有明显冠脉痉挛的患者，可用至20-30mg，一日3-4次。最大剂量不宜超过120mg/日。如果病情紧急，可嚼碎服或舌下含服10mg，根据患者对药物的反应，决定再次给药。",
        "图片": "https://example.com/images/nifedipine.jpg",
        "副作用": "常见服药后出现外周水肿（外周水肿与剂量相关，服用60mg/日时的发生率为4%，服用120mg/日则为12.5%）；头晕；头痛；恶心；乏力和面部潮红（10%）。一过性低血压（5%），多不需要停药（一过性低血压与剂量相关，在剂量<60mg/日时的发生率为2%，而120mg/日的发生率为5%）。个别患者发生心绞痛，可能与低血压反应有关。还可见心悸；鼻塞；胸闷；气短；便秘；腹泻；胃肠痉挛；腹胀；骨骼肌发炎；关节僵硬；肌肉痉挛；精神紧张；颤抖；神经过敏；睡眠紊乱；视力模糊；平衡失调等（2%）。晕厥（0.5%），减量或与其他抗心绞痛药合用则不再发生。",
        "注意事项": "低血压。绝大多数患者服用硝苯地平后仅有轻度低血压反应，个别患者出现严重的低血压症状。这种反应常发生在剂量调整期或加量时，特别是合用β-受体阻滞剂时。在此期间需监测血压，尤其合用其他降压药时；芬太尼麻醉接受冠脉旁路血管移植术(或者其他手术)的患者，单独服用硝苯地平或与β-受体阻滞剂合用可导致严重的低血压，如条件许可应至少停药36小时；心绞痛和/或心肌梗死极少数患者，特别是严重冠脉狭窄患者，在服用硝苯地平或加量期间，降压后出现反射性交感兴奋而心率加快，心绞痛或心肌梗死的发生率增加；外周水肿；β-受体阻滞剂'反跳'症状；充血性心力衰竭；对诊断的干扰；肝肾功能不全、正在服用β-受体阻滞剂者应慎用，宜从小剂量开始，以防诱发或加重低血压，增加心绞痛、心力衰竭、甚至心肌梗死的发生率。慢性肾衰患者应用本品时偶有可逆性血尿素氮和肌酐升高，与硝苯地平的关系不够明确。"
    },
    "盐酸氟桂利嗪": {
        "功效": "脑供血不足，椎动脉缺血，脑血栓形成后等；耳鸣，脑晕；偏头痛预防；癫痫辅助治疗。",
        "用法": "口服。偏头痛的预防性治疗：起始剂量：对于65岁以下患者开始治疗时可给予每晚2粒，65岁以上患者每晚1粒。如在治疗中出现抑郁、锥体外系反应和其它无法接受的不良反应，应及时停药。如在治疗2个月后未见明显改善，则可视为病人对本品无反应，可停止用药；眩晕：每日剂量应与上相同，但应在控制症状后及时停药，初次疗程通常少于2个月。",
        "图片": "https://example.com/images/flunarizine.jpg",
        "副作用": "最常见的不良反应为：嗜睡和疲惫，某些患者还可出现体重增加（或伴有食欲增加），这些反应常为一过性的；长期用药时，偶见下列严重的不良反应：抑郁症，有抑郁病史的女性患者尤其易发生此反应；锥体外系症状（如运动徐缓、强直、静坐不能、口颌运动障碍、震颤等），老年人较易发生；少见的不良反应报道有：胃肠道反应：胃灼热、恶心、胃痛；中枢神经系统：失眠、焦虑；其它：溢乳、口干、肌肉疼痛及皮疹。",
        "注意事项": "用药后疲惫症状逐步加重者应当减量或停药；严格控制药物剂量，当应用维持剂量达不到治疗效果或长期应用出现锥体外系症状时，应当减量或停服药；患有帕金森病等锥体外系疾病时，应当慎用本制剂；由于本制剂可随乳汁分泌，虽然尚无致畸和对胚胎发育有影响的研究报告，但原则上孕妇和哺乳期妇女不用此药；驾驶员和机械操作者慎用，以免发生意外。"
    }
}

# 模拟疾病-药物推荐数据库
MOCK_DISEASE_MEDICATION_RECOMMENDATIONS = {
    "头痛": ["布洛芬", "阿司匹林", "对乙酰氨基酚"],
    "发热": ["布洛芬", "对乙酰氨基酚", "阿司匹林"],
    "感冒": ["布洛芬", "对乙酰氨基酚", "盐酸氨溴索"],
    "咳嗽": ["盐酸氨溴索"],
    "过敏": ["盐酸左西替利嗪"],
    "高血压": ["硝苯地平"],
    "糖尿病": ["盐酸二甲双胍"],
    "偏头痛": ["布洛芬", "盐酸氟桂利嗪"],
    "关节痛": ["布洛芬", "阿司匹林"],
    "牙痛": ["布洛芬", "对乙酰氨基酚", "阿司匹林"],
    "胃痛": [],
    "腹泻": [],
    "便秘": [],
    "失眠": [],
    "焦虑": [],
    "抑郁": [],
    "眩晕": ["盐酸氟桂利嗪"],
    "耳鸣": ["盐酸氟桂利嗪"],
    "鼻塞": [],
    "流涕": [],
    "喉咙痛": ["布洛芬", "阿司匹林"]
}

# 搜索药物详细信息
def search_medication_details(medication_name: str) -> Optional[Dict[str, Any]]:
    """
    搜索药物的详细信息
    在实际应用中，这里可以调用外部API获取真实的药物信息
    目前使用模拟数据库
    """
    try:
        # 转换为小写以实现不区分大小写的搜索
        medication_name = medication_name.strip()
        
        # 首先尝试精确匹配
        if medication_name in MOCK_MEDICATION_DATABASE:
            return MOCK_MEDICATION_DATABASE[medication_name]
        
        # 尝试模糊匹配（包含关系）
        for key, value in MOCK_MEDICATION_DATABASE.items():
            if medication_name in key or key in medication_name:
                return value
        
        # 如果没有找到匹配的药物，尝试调用外部API
        # 注意：这只是一个示例，实际应用中需要替换为真实的API
        # external_result = call_external_medication_api(medication_name)
        # if external_result:
        #     return external_result
        
        logger.warning(f"未找到药物 '{medication_name}' 的详细信息")
        return None
    except Exception as e:
        logger.error(f"搜索药物信息时发生错误: {str(e)}")
        return None

# 获取疾病推荐的药物列表
def get_recommended_medications_for_disease(disease_name: str) -> List[str]:
    """
    获取特定疾病推荐的药物列表
    在实际应用中，这里可以调用外部API获取真实的推荐信息
    目前使用模拟数据库
    """
    try:
        # 转换为小写以实现不区分大小写的搜索
        disease_name = disease_name.strip()
        
        # 首先尝试精确匹配
        if disease_name in MOCK_DISEASE_MEDICATION_RECOMMENDATIONS:
            return MOCK_DISEASE_MEDICATION_RECOMMENDATIONS[disease_name]
        
        # 尝试模糊匹配（包含关系）
        for key, value in MOCK_DISEASE_MEDICATION_RECOMMENDATIONS.items():
            if disease_name in key or key in disease_name:
                return value
        
        # 如果没有找到匹配的疾病，尝试调用外部API
        # 注意：这只是一个示例，实际应用中需要替换为真实的API
        # external_result = call_external_disease_api(disease_name)
        # if external_result:
        #     return external_result
        
        logger.warning(f"未找到疾病 '{disease_name}' 的推荐药物")
        return []
    except Exception as e:
        logger.error(f"获取疾病推荐药物时发生错误: {str(e)}")
        return []

# （示例）调用外部药物API的函数
# 注意：这只是一个示例，实际应用中需要替换为真实的API调用
# def call_external_medication_api(medication_name: str) -> Optional[Dict[str, Any]]:
#     try:
#         # 这里应该是真实的API调用代码
#         logger.info(f"调用外部API搜索药物 '{medication_name}'")
#         
#         # 模拟API调用延迟
#         # import time
#         # time.sleep(1)
#         
#         # 模拟API响应
#         # response = requests.get(
#         #     f"https://api.medication-info.com/search",
#         #     params={"name": medication_name},
#         #     headers={"Authorization": "Bearer YOUR_API_KEY"}
#         # )
#         # 
#         # if response.status_code == 200:
#         #     data = response.json()
#         #     # 处理API返回的数据，转换为我们需要的格式
#         #     return {
#         #         "功效": data.get("indications", ""),
#         #         "用法": data.get("dosage", ""),
#         #         "图片": data.get("image_url", ""),
#         #         "副作用": data.get("side_effects", ""),
#         #         "注意事项": data.get("precautions", "")
#         #     }
#         
#         return None
#     except Exception as e:
#         logger.error(f"调用外部药物API时发生错误: {str(e)}")
#         return None

# 批量搜索药物信息
def batch_search_medication_details(medication_names: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    批量搜索药物的详细信息
    """
    results = {}
    
    for name in medication_names:
        results[name] = search_medication_details(name)
    
    return results

# 验证药物名称是否有效
def validate_medication_name(medication_name: str) -> bool:
    """
    验证药物名称是否有效
    """
    if not medication_name or not isinstance(medication_name, str):
        return False
    
    # 检查是否包含非法字符
    import re
    if re.search(r'[^\u4e00-\u9fa5a-zA-Z0-9\-\(\)\[\]]', medication_name):
        return False
    
    # 检查长度是否合理
    if len(medication_name) < 2 or len(medication_name) > 50:
        return False
    
    return True

# 格式化药物信息输出
def format_medication_info(medication_info: Dict[str, Any]) -> str:
    """
    格式化药物信息为可读的字符串
    """
    if not medication_info:
        return "未找到药物信息"
    
    formatted_info = []
    
    if "功效" in medication_info and medication_info["功效"]:
        formatted_info.append(f"【功效】{medication_info['功效']}")
    
    if "用法" in medication_info and medication_info["用法"]:
        formatted_info.append(f"【用法】{medication_info['用法']}")
    
    if "副作用" in medication_info and medication_info["副作用"]:
        formatted_info.append(f"【副作用】{medication_info['副作用']}")
    
    if "注意事项" in medication_info and medication_info["注意事项"]:
        formatted_info.append(f"【注意事项】{medication_info['注意事项']}")
    
    return "\n".join(formatted_info)

# 从药物名称推测药物类型
def infer_medication_type(medication_name: str) -> str:
    """
    从药物名称推测药物类型
    """
    # 常见药物类型关键词
    type_keywords = {
        "抗生素": ["头孢", "青霉素", "霉素", "菌素", "沙星", "环素", "硝唑", "磺胺"],
        "止痛药": ["布洛芬", "对乙酰氨基酚", "阿司匹林", "吗啡", "可待因", "曲马多", "芬太尼"],
        "退烧药": ["布洛芬", "对乙酰氨基酚", "阿司匹林"],
        "降压药": ["地平", "洛尔", "普利", "沙坦", "噻嗪", "胍", "利血平"],
        "降糖药": ["双胍", "格列", "列奈", "波糖", "胰岛素"],
        "抗过敏药": ["氯雷他定", "西替利嗪", "扑尔敏", "苯海拉明", "异丙嗪"],
        "感冒药": ["感冒", "氨酚", "烷胺", "伪麻", "那敏"],
        "消化系统药": ["拉唑", "替丁", "吗丁啉", "思密达", "胃舒平", "酵母", "乳酶生"],
        "呼吸系统药": ["氨溴索", "氯化铵", "可待因", "右美沙芬", "沙丁胺醇", "布地奈德"],
        "心血管药": ["心", "冠", "舒", "救心丸", "丹参", "硝酸甘油", "银杏叶"],
        "神经系统药": ["氟桂利嗪", "西比灵", "安定", "舒乐安定", "苯巴比妥", "卡马西平"],
        "维生素类": ["维生素", "VA", "VB", "VC", "VD", "VE", "VK", "钙片", "铁剂", "锌剂"]
    }
    
    # 遍历关键词，查找匹配
    for med_type, keywords in type_keywords.items():
        for keyword in keywords:
            if keyword in medication_name:
                return med_type
    
    # 如果没有匹配到已知类型，返回默认类型
    return "其他"

# 导出药物数据库（用于备份或迁移）
def export_medication_database(file_path: str) -> bool:
    """
    导出药物数据库到文件
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(MOCK_MEDICATION_DATABASE, f, ensure_ascii=False, indent=2)
        logger.info(f"药物数据库已导出到 {file_path}")
        return True
    except Exception as e:
        logger.error(f"导出药物数据库时发生错误: {str(e)}")
        return False

# 导入药物数据库（用于恢复或更新）
def import_medication_database(file_path: str) -> bool:
    """
    从文件导入药物数据库
    """
    try:
        global MOCK_MEDICATION_DATABASE
        
        with open(file_path, 'r', encoding='utf-8') as f:
            imported_data = json.load(f)
        
        # 验证导入的数据格式
        if not isinstance(imported_data, dict):
            raise ValueError("导入的数据格式不正确")
        
        # 更新数据库
        MOCK_MEDICATION_DATABASE = imported_data
        logger.info(f"药物数据库已从 {file_path} 导入")
        return True
    except Exception as e:
        logger.error(f"导入药物数据库时发生错误: {str(e)}")
        return False