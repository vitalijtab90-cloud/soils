import streamlit as st
import pandas as pd
import random
import io

class SoilModelGeneratorStreamlit:
    def __init__(self):
        self.df = None
        
    def generate_color_triplet(self, num_variants):
        """Генерация цветов для строки"""
        r1 = random.randint(50, 255)
        g1 = random.randint(50, 255)
        b1 = random.randint(50, 255)
        colors = [r1 + g1 * 256 + b1 * 65536]
        
        for i in range(1, num_variants):
            factor = 0.6 + (i * 0.2)
            r = min(int(r1 * factor), 255)
            g = min(int(g1 * factor), 255)
            b = min(int(b1 * factor), 255)
            colors.append(r + g * 256 + b * 65536)
            
        return colors
    
    def round_value(self, value):
        """Округление численных значений до 2 знаков"""
        try:
            if pd.isna(value):
                return 0
            if isinstance(value, str):
                return value
            return round(float(value), 2)
        except (ValueError, TypeError):
            return value if isinstance(value, str) else 0
    
    def generate_soil_model_file(self, filtered_df, colors_dict, prob, int_flag, e3_flag, e5_flag):
        """Генерация основного файла с Soil Model"""
        output_lines = []
        
        for idx, row in filtered_df.iterrows():
            layer_num = str(row.iloc[0]) if pd.notna(row.iloc[0]) else f"Row_{idx}"
            colors = colors_dict[idx]
            color_idx = 0
            
            # Определяем столбцы в зависимости от вероятности
            if prob == "0.85":
                phi_col = 5
                c_col = 6
                gamma_unsat_col = 16
            else:  # 0.95
                phi_col = 8
                c_col = 9
                gamma_unsat_col = 18
            
            # Базовый материал
            output_lines.extend([
                '_soilmat "SoilModel" 2',
                f'set SoilMat_1.Identification "MC_{layer_num}"',
                f'_set MC_{layer_num}.Colour {colors[color_idx]}',
                f'_set MC_{layer_num}.gammaUnsat {self.round_value(row.iloc[gamma_unsat_col])}',
                f'_set MC_{layer_num}.gammaSat {self.round_value(row.iloc[13])}',
                f'_set MC_{layer_num}.ERef {self.round_value(row.iloc[10])}',
                f'_set MC_{layer_num}.nu {self.round_value(row.iloc[12])}',
                f'_set MC_{layer_num}.cRef {self.round_value(row.iloc[c_col])}',
                f'_set MC_{layer_num}.phi {self.round_value(row.iloc[phi_col])}',
                f'_set MC_{layer_num}.eInit {self.round_value(row.iloc[21])}'
            ])
            color_idx += 1
            
            # Материал int
            if int_flag and color_idx < len(colors):
                output_lines.extend([
                    '_soilmat "SoilModel" 2',
                    f'set SoilMat_1.Identification "MC_{layer_num}_int"',
                    f'_set MC_{layer_num}_int.Colour {colors[color_idx]}',
                    f'_set MC_{layer_num}_int.gammaUnsat {self.round_value(row.iloc[gamma_unsat_col])}',
                    f'_set MC_{layer_num}_int.gammaSat {self.round_value(row.iloc[13])}',
                    f'_set MC_{layer_num}_int.ERef {self.round_value(row.iloc[10])}',
                    f'_set MC_{layer_num}_int.nu {self.round_value(row.iloc[12])}',
                    f'_set MC_{layer_num}_int.cRef 1',
                    f'_set MC_{layer_num}_int.phi {self.round_value(row.iloc[31])}',
                    f'_set MC_{layer_num}_int.eInit {self.round_value(row.iloc[21])}'
                ])
                color_idx += 1
            
            # Материал 3E
            if e3_flag and color_idx < len(colors):
                output_lines.extend([
                    '_soilmat "SoilModel" 2',
                    f'set SoilMat_1.Identification "MC_{layer_num}_3E"',
                    f'_set MC_{layer_num}_3E.Colour {colors[color_idx]}',
                    f'_set MC_{layer_num}_3E.gammaUnsat {self.round_value(row.iloc[gamma_unsat_col])}',
                    f'_set MC_{layer_num}_3E.gammaSat {self.round_value(row.iloc[13])}',
                    f'_set MC_{layer_num}_3E.ERef {self.round_value(row.iloc[30])}',
                    f'_set MC_{layer_num}_3E.nu 0.2',
                    f'_set MC_{layer_num}_3E.cRef {self.round_value(row.iloc[c_col])}',
                    f'_set MC_{layer_num}_3E.phi {self.round_value(row.iloc[phi_col])}',
                    f'_set MC_{layer_num}_3E.eInit {self.round_value(row.iloc[21])}'
                ])
                color_idx += 1
            
            # Материал 5E
            if e5_flag and color_idx < len(colors):
                output_lines.extend([
                    '_soilmat "SoilModel" 2',
                    f'set SoilMat_1.Identification "MC_{layer_num}_5E"',
                    f'_set MC_{layer_num}_5E.Colour {colors[color_idx]}',
                    f'_set MC_{layer_num}_5E.gammaUnsat {self.round_value(row.iloc[gamma_unsat_col])}',
                    f'_set MC_{layer_num}_5E.gammaSat {self.round_value(row.iloc[13])}',
                    f'_set MC_{layer_num}_5E.ERef {self.round_value(row.iloc[29])}',
                    f'_set MC_{layer_num}_5E.nu 0.2',
                    f'_set MC_{layer_num}_5E.cRef {self.round_value(row.iloc[c_col])}',
                    f'_set MC_{layer_num}_5E.phi {self.round_value(row.iloc[phi_col])}',
                    f'_set MC_{layer_num}_5E.eInit {self.round_value(row.iloc[21])}'
                ])
        
        return "\n".join(output_lines)
    
    def generate_sba_file(self, filtered_df):
        """Генерация .sba файла"""
        output_lines = [str(len(filtered_df))]
        
        # Поиск столбцов AS:AY (индексы 44-50)
        as_ay_indices = [i for i in range(44, 51) if i < len(filtered_df.columns)]
        
        if as_ay_indices:
            for col_idx in as_ay_indices:
                for idx, row in filtered_df.iterrows():
                    value = self.round_value(row.iloc[col_idx])
                    output_lines.append(str(value))
            
            return "\n".join(output_lines)
        else:
            return None

# Streamlit интерфейс
def main():
    st.set_page_config(page_title="Генератор Soil Model", page_icon="🎨", layout="wide")
    
    st.title("🎨 Генератор Soil Model")
    st.markdown("---")
    
    generator = SoilModelGeneratorStreamlit()
    
    # Загрузка файла
    uploaded_file = st.file_uploader("📤 Загрузите Excel файл", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            generator.df = pd.read_excel(uploaded_file, header=2)
            st.success(f"✅ Файл '{uploaded_file.name}' успешно загружен!")
            
            # Показываем информацию о столбцах
            with st.expander("📊 Информация о данных"):
                st.write(f"Количество строк: {len(generator.df)}")
                st.write("Столбцы:", list(generator.df.columns))
            
            # Выбор параметров
            st.subheader("🎯 Параметры генерации")
            
            col1, col2 = st.columns(2)
            
            with col1:
                prob_value = st.radio("Доверительная вероятность:", ['0.85', '0.95'], index=0)
            
            with col2:
                st.write("Дополнительные опции:")
                int_flag = st.checkbox("int")
                e3_flag = st.checkbox("3E")
                e5_flag = st.checkbox("5E")
                wall_flag = st.checkbox("Wall")
            
            # Выбор грунтов
            st.subheader("🏗️ Выбор грунтов")
            
            if 'selected_soils' not in st.session_state:
                st.session_state.selected_soils = []
            
            # Чекбоксы для выбора грунтов
            selected_indices = []
            for idx, row in generator.df.iterrows():
                layer_num = str(row.iloc[0]) if pd.notna(row.iloc[0]) else f"Row_{idx}"
                if st.checkbox(f"Грунт {layer_num}", key=f"soil_{idx}"):
                    selected_indices.append(idx)
            
            # Кнопка генерации
            if st.button("🚀 Сгенерировать файлы", type="primary"):
                if not selected_indices:
                    st.error("❌ Не выбрано ни одного грунта!")
                    return
                
                # Создаем уменьшенную таблицу
                filtered_df = generator.df.iloc[selected_indices].copy()
                
                # Генерируем цвета
                colors_dict = {}
                for idx in filtered_df.index:
                    num_colors = 1
                    if int_flag: num_colors += 1
                    if e3_flag: num_colors += 1
                    if e5_flag: num_colors += 1
                    colors_dict[idx] = generator.generate_color_triplet(num_colors)
                
                # Генерируем основной файл
                soil_model_content = generator.generate_soil_model_file(
                    filtered_df, colors_dict, prob_value, int_flag, e3_flag, e5_flag
                )
                
                # Скачивание основного файла
                st.download_button(
                    label="📥 Скачать Soil Model файл",
                    data=soil_model_content,
                    file_name="soil_model_output.txt",
                    mime="text/plain"
                )
                
                # Генерируем .sba файл если нужно
                if wall_flag:
                    sba_content = generator.generate_sba_file(filtered_df)
                    if sba_content:
                        st.download_button(
                            label="📥 Скачать Wall Data (.sba)",
                            data=sba_content,
                            file_name="wall_data.sba",
                            mime="text/plain"
                        )
                    else:
                        st.warning("❌ Столбцы AS:AY не найдены в данных!")
                
                st.success("✅ Файлы успешно сгенерированы!")
                
                # Показываем превью
                with st.expander("👀 Предварительный просмотр Soil Model файла"):
                    st.code(soil_model_content[:2000] + "..." if len(soil_model_content) > 2000 else soil_model_content)
                        
        except Exception as e:
            st.error(f"❌ Ошибка при обработке файла: {str(e)}")
    else:
        st.info("📝 Пожалуйста, загрузите Excel файл для начала работы")

if __name__ == "__main__":
    main()