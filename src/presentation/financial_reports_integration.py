"""
Financial Reports Integration.
Integración de informes financieros con el sistema de menús existente.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from src.infrastructure.factories.financial_reports_factory import FinancialReportsFactory
from src.application.services.FinancialReportsService import FinancialReportsService
from src.application.ports.interfaces import Logger


class FinancialReportsIntegration:
    """
    Clase de integración para conectar informes financieros con el sistema principal.
    """
    
    def __init__(
        self,
        financial_reports_service: FinancialReportsService,
        logger: Logger
    ):
        """
        Inicializar integración.
        
        Args:
            financial_reports_service: Servicio principal de informes financieros
            logger: Logger para registrar operaciones
        """
        self._service = financial_reports_service
        self._logger = logger
    
    # ========================================================================================
    # MÉTODOS PARA EL MENÚ PRINCIPAL - ESTADO DE RESULTADOS
    # ========================================================================================
    
    def generar_estado_resultados_interactivo(self) -> Dict[str, Any]:
        """
        Generar Estado de Resultados con interacción de usuario.
        Método para ser llamado desde el menú principal.
        
        Returns:
            Resultado de la operación con información para mostrar al usuario
        """
        try:
            self._logger.info("Iniciando generación interactiva de Estado de Resultados")
            
            # Mostrar períodos sugeridos
            periodos_sugeridos = self._service.get_tipos_periodo_sugeridos()
            
            print("\n" + "="*70)
            print("               GENERACIÓN DE ESTADO DE RESULTADOS")
            print("="*70)
            
            print("\nPeríodos sugeridos:")
            for idx, (key, periodo) in enumerate(periodos_sugeridos.items(), 1):
                print(f"{idx}. {periodo['nombre']} ({periodo['fecha_inicio']} - {periodo['fecha_fin']})")
            
            print(f"{len(periodos_sugeridos) + 1}. Personalizar período")
            
            # Solicitar selección
            while True:
                try:
                    seleccion = input(f"\nSeleccione una opción (1-{len(periodos_sugeridos) + 1}): ").strip()
                    
                    if seleccion.isdigit():
                        opcion = int(seleccion)
                        if 1 <= opcion <= len(periodos_sugeridos):
                            # Usar período sugerido
                            periodo_keys = list(periodos_sugeridos.keys())
                            periodo_seleccionado = periodos_sugeridos[periodo_keys[opcion - 1]]
                            fecha_inicio = periodo_seleccionado['fecha_inicio']
                            fecha_fin = periodo_seleccionado['fecha_fin']
                            break
                        elif opcion == len(periodos_sugeridos) + 1:
                            # Período personalizado
                            fecha_inicio = input("Ingrese fecha inicio (YYYY-MM-DD): ").strip()
                            fecha_fin = input("Ingrese fecha fin (YYYY-MM-DD): ").strip()
                            
                            # Validar fechas
                            validacion = self._service.validar_parametros_estado_resultados(fecha_inicio, fecha_fin)
                            if validacion['valid']:
                                break
                            else:
                                print("❌ Errores en las fechas:")
                                for error in validacion['errors']:
                                    print(f"   • {error}")
                                continue
                        else:
                            print("❌ Opción inválida")
                            continue
                    else:
                        print("❌ Ingrese un número válido")
                        continue
                        
                except KeyboardInterrupt:
                    return {"success": False, "message": "Operación cancelada por el usuario"}
            
            # Solicitar formato de salida
            formatos = self._service.get_formatos_disponibles()
            print(f"\nFormatos disponibles: {', '.join(formatos)}")
            formato = input("Formato de salida (json/csv) [json]: ").strip().lower() or "json"
            
            if formato not in formatos:
                formato = "json"
                print(f"Formato inválido, usando {formato}")
            
            # Generar informe
            print(f"\n🔄 Generando Estado de Resultados para período {fecha_inicio} - {fecha_fin}...")
            
            response = self._service.generar_estado_resultados(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                formato_salida=formato,
                incluir_kpis=True
            )
            
            if response.success:
                self._mostrar_resultado_estado_resultados(response)
                return {
                    "success": True,
                    "message": "Estado de Resultados generado exitosamente",
                    "data": response.data,
                    "file_path": response.file_path,
                    "execution_time": response.execution_time_seconds
                }
            else:
                print(f"❌ Error: {response.message}")
                return {
                    "success": False,
                    "message": response.message
                }
                
        except Exception as e:
            error_msg = f"Error generando Estado de Resultados: {str(e)}"
            self._logger.error(error_msg)
            print(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    # ========================================================================================
    # MÉTODOS PARA EL MENÚ PRINCIPAL - ESTADO DE SITUACIÓN FINANCIERA
    # ========================================================================================
    
    def generar_balance_general_interactivo(self) -> Dict[str, Any]:
        """
        Generar Estado de Situación Financiera con interacción de usuario.
        Método para ser llamado desde el menú principal.
        
        Returns:
            Resultado de la operación
        """
        try:
            self._logger.info("Iniciando generación interactiva de Estado de Situación Financiera")
            
            # Mostrar fechas sugeridas
            fechas_sugeridas = self._service.get_fechas_corte_sugeridas()
            
            print("\n" + "="*70)
            print("                  GENERACIÓN DE ESTADO DE SITUACIÓN FINANCIERA")
            print("="*70)
            
            print("\nFechas de corte sugeridas:")
            for idx, (key, fecha) in enumerate(fechas_sugeridas.items(), 1):
                print(f"{idx}. {key.replace('_', ' ').title()}: {fecha}")
            
            print(f"{len(fechas_sugeridas) + 1}. Personalizar fecha")
            
            # Solicitar selección
            while True:
                try:
                    seleccion = input(f"\nSeleccione una opción (1-{len(fechas_sugeridas) + 1}): ").strip()
                    
                    if seleccion.isdigit():
                        opcion = int(seleccion)
                        if 1 <= opcion <= len(fechas_sugeridas):
                            # Usar fecha sugerida
                            fecha_keys = list(fechas_sugeridas.keys())
                            fecha_corte = fechas_sugeridas[fecha_keys[opcion - 1]]
                            break
                        elif opcion == len(fechas_sugeridas) + 1:
                            # Fecha personalizada
                            fecha_corte = input("Ingrese fecha de corte (YYYY-MM-DD): ").strip()
                            
                            # Validar fecha
                            validacion = self._service.validar_parametros_balance_general(fecha_corte)
                            if validacion['valid']:
                                break
                            else:
                                print("❌ Errores en la fecha:")
                                for error in validacion['errors']:
                                    print(f"   • {error}")
                                continue
                        else:
                            print("❌ Opción inválida")
                            continue
                    else:
                        print("❌ Ingrese un número válido")
                        continue
                        
                except KeyboardInterrupt:
                    return {"success": False, "message": "Operación cancelada por el usuario"}
            
            # Solicitar opciones adicionales
            incluir_detalle = input("¿Incluir detalle de cuentas? (s/n) [n]: ").strip().lower() in ['s', 'sí', 'si', 'y', 'yes']
            
            formatos = self._service.get_formatos_disponibles()
            print(f"\nFormatos disponibles: {', '.join(formatos)}")
            formato = input("Formato de salida (json/csv) [json]: ").strip().lower() or "json"
            
            if formato not in formatos:
                formato = "json"
                print(f"Formato inválido, usando {formato}")
            
            # Generar informe
            print(f"\n🔄 Generando Estado de Situación Financiera para fecha {fecha_corte}...")
            
            response = self._service.generar_balance_general(
                fecha_corte=fecha_corte,
                formato_salida=formato,
                incluir_kpis=True,
                incluir_detalle=incluir_detalle
            )
            
            if response.success:
                self._mostrar_resultado_balance_general(response)
                return {
                    "success": True,
                    "message": "Estado de Situación Financiera generado exitosamente",
                    "data": response.data,
                    "file_path": response.file_path,
                    "execution_time": response.execution_time_seconds
                }
            else:
                print(f"❌ Error: {response.message}")
                return {
                    "success": False,
                    "message": response.message
                }
                
        except Exception as e:
            error_msg = f"Error generando Estado de Situación Financiera: {str(e)}"
            self._logger.error(error_msg)
            print(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    # ========================================================================================
    # MÉTODOS PARA EL MENÚ PRINCIPAL - INFORME COMPLETO
    # ========================================================================================
    
    def generar_informe_completo_interactivo(self) -> Dict[str, Any]:
        """
        Generar informe financiero completo con interacción de usuario.
        
        Returns:
            Resultado de la operación
        """
        try:
            self._logger.info("Iniciando generación interactiva de informe financiero completo")
            
            print("\n" + "="*70)
            print("            GENERACIÓN DE INFORME FINANCIERO COMPLETO")
            print("="*70)
            print("Este informe incluye Estado de Resultados + Estado de Situación Financiera + KPIs")
            
            # Solicitar período para Estado de Resultados
            periodos_sugeridos = self._service.get_tipos_periodo_sugeridos()
            
            print("\n1️⃣ PERÍODO PARA ESTADO DE RESULTADOS")
            print("Períodos sugeridos:")
            for idx, (key, periodo) in enumerate(periodos_sugeridos.items(), 1):
                print(f"{idx}. {periodo['nombre']} ({periodo['fecha_inicio']} - {periodo['fecha_fin']})")
            
            print(f"{len(periodos_sugeridos) + 1}. Personalizar período")
            
            # Selección del período
            while True:
                try:
                    seleccion = input(f"\nSeleccione período (1-{len(periodos_sugeridos) + 1}): ").strip()
                    
                    if seleccion.isdigit():
                        opcion = int(seleccion)
                        if 1 <= opcion <= len(periodos_sugeridos):
                            periodo_keys = list(periodos_sugeridos.keys())
                            periodo_seleccionado = periodos_sugeridos[periodo_keys[opcion - 1]]
                            fecha_inicio = periodo_seleccionado['fecha_inicio']
                            fecha_fin = periodo_seleccionado['fecha_fin']
                            break
                        elif opcion == len(periodos_sugeridos) + 1:
                            fecha_inicio = input("Fecha inicio Estado de Resultados (YYYY-MM-DD): ").strip()
                            fecha_fin = input("Fecha fin Estado de Resultados (YYYY-MM-DD): ").strip()
                            
                            validacion = self._service.validar_parametros_estado_resultados(fecha_inicio, fecha_fin)
                            if validacion['valid']:
                                break
                            else:
                                print("❌ Errores en las fechas:")
                                for error in validacion['errors']:
                                    print(f"   • {error}")
                                continue
                        else:
                            print("❌ Opción inválida")
                            continue
                    else:
                        print("❌ Ingrese un número válido")
                        continue
                        
                except KeyboardInterrupt:
                    return {"success": False, "message": "Operación cancelada por el usuario"}
            
            # Solicitar fecha de corte para Estado de Situación Financiera
            fechas_sugeridas = self._service.get_fechas_corte_sugeridas()
            
            print("\n2️⃣ FECHA DE CORTE PARA ESTADO DE SITUACIÓN FINANCIERA")
            for idx, (key, fecha) in enumerate(fechas_sugeridas.items(), 1):
                print(f"{idx}. {key.replace('_', ' ').title()}: {fecha}")
            
            print(f"{len(fechas_sugeridas) + 1}. Personalizar fecha")
            
            # Selección de fecha de corte
            while True:
                try:
                    seleccion = input(f"\nSeleccione fecha corte (1-{len(fechas_sugeridas) + 1}): ").strip()
                    
                    if seleccion.isdigit():
                        opcion = int(seleccion)
                        if 1 <= opcion <= len(fechas_sugeridas):
                            fecha_keys = list(fechas_sugeridas.keys())
                            fecha_corte_balance = fechas_sugeridas[fecha_keys[opcion - 1]]
                            break
                        elif opcion == len(fechas_sugeridas) + 1:
                            fecha_corte_balance = input("Fecha corte Estado de Situación Financiera (YYYY-MM-DD): ").strip()
                            
                            validacion = self._service.validar_parametros_balance_general(fecha_corte_balance)
                            if validacion['valid']:
                                break
                            else:
                                print("❌ Errores en la fecha:")
                                for error in validacion['errors']:
                                    print(f"   • {error}")
                                continue
                        else:
                            print("❌ Opción inválida")
                            continue
                    else:
                        print("❌ Ingrese un número válido")
                        continue
                        
                except KeyboardInterrupt:
                    return {"success": False, "message": "Operación cancelada por el usuario"}
            
            # Formato de salida
            formatos = self._service.get_formatos_disponibles()
            print(f"\n3️⃣ FORMATO DE SALIDA")
            print(f"Formatos disponibles: {', '.join(formatos)}")
            formato = input("Formato de salida (json/csv) [json]: ").strip().lower() or "json"
            
            if formato not in formatos:
                formato = "json"
                print(f"Formato inválido, usando {formato}")
            
            # Generar informe
            print(f"\n🔄 Generando informe financiero completo...")
            print(f"   📊 Estado de Resultados: {fecha_inicio} - {fecha_fin}")
            print(f"   💰 Estado de Situación Financiera: {fecha_corte_balance}")
            
            response = self._service.generar_informe_completo(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                fecha_corte_balance=fecha_corte_balance,
                formato_salida=formato
            )
            
            if response.success:
                self._mostrar_resultado_informe_completo(response)
                return {
                    "success": True,
                    "message": "Informe financiero completo generado exitosamente",
                    "data": response.data,
                    "file_path": response.file_path,
                    "execution_time": response.execution_time_seconds
                }
            else:
                print(f"❌ Error: {response.message}")
                return {
                    "success": False,
                    "message": response.message
                }
                
        except Exception as e:
            error_msg = f"Error generando informe completo: {str(e)}"
            self._logger.error(error_msg)
            print(f"❌ {error_msg}")
            return {"success": False, "message": error_msg}
    
    # ========================================================================================
    # MÉTODOS AUXILIARES PARA MOSTRAR RESULTADOS
    # ========================================================================================
    
    def _mostrar_resultado_estado_resultados(self, response) -> None:
        """Mostrar resultado del Estado de Resultados en consola."""
        if not response.data or "estado_resultados" not in response.data:
            print("❌ No se pudo obtener datos del Estado de Resultados")
            return
        
        estado = response.data["estado_resultados"]
        
        print("\n" + "="*70)
        print("                    ESTADO DE RESULTADOS")
        print("="*70)
        print(f"Período: {estado['fecha_inicio']} - {estado['fecha_fin']}")
        print(f"Moneda: {estado['moneda']}")
        print("-"*70)
        
        # Formatear números con comas decimales
        ventas = f"{estado['ventas_netas']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        costo = f"{estado['costo_ventas']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        utilidad_bruta = f"{estado['utilidad_bruta']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        gastos = f"{estado['gastos_operativos']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        utilidad_neta = f"{estado['utilidad_neta']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        print(f"Ventas Netas:              $ {ventas}")
        print(f"Costo de Ventas:           $ {costo}")
        print(f"Utilidad Bruta:            $ {utilidad_bruta}")
        print(f"Gastos Operativos:         $ {gastos}")
        print(f"Utilidad Neta:             $ {utilidad_neta}")
        print("-"*70)
        print(f"Margen Bruto:              {estado['margen_bruto_porcentaje']:.2f}%")
        print(f"Margen Neto:               {estado['margen_neto_porcentaje']:.2f}%")
        
        # Mostrar KPIs si están disponibles
        if "kpis" in response.data:
            kpis = response.data["kpis"]
            print("-"*70)
            print("KPIs ADICIONALES:")
            print(f"Eficiencia Operativa:      {kpis.get('eficiencia_operativa', 0):.2f}%")
        
        print("="*70)
        print(f"✅ Informe generado en {response.execution_time_seconds:.2f} segundos")
        if response.file_path:
            print(f"📄 Archivo guardado: {response.file_path}")
        print()
    
    def _mostrar_resultado_balance_general(self, response) -> None:
        """Mostrar resultado del Estado de Situación Financiera en consola."""
        if not response.data or "balance_general" not in response.data:
            print("❌ No se pudo obtener datos del Estado de Situación Financiera")
            return
        
        balance = response.data["balance_general"]
        
        print("\n" + "="*70)
        print("                      ESTADO DE SITUACIÓN FINANCIERA")
        print("="*70)
        print(f"Fecha de Corte: {balance['fecha_corte']}")
        print(f"Moneda: {balance['moneda']}")
        print("-"*70)
        
        # Formatear números
        act_corr = f"{balance['activos_corrientes']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        act_no_corr = f"{balance['activos_no_corrientes']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        total_act = f"{balance['total_activos']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        pas_corr = f"{balance['pasivos_corrientes']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        pas_no_corr = f"{balance['pasivos_no_corrientes']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        total_pas = f"{balance['total_pasivos']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        capital = f"{balance['capital']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        util_ret = f"{balance['utilidades_retenidas']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        util_ej = f"{balance['utilidades_ejercicio']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        total_pat = f"{balance['total_patrimonio']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        print("ACTIVOS:")
        print(f"  Corrientes:              $ {act_corr}")
        print(f"  No Corrientes:           $ {act_no_corr}")
        print(f"  TOTAL ACTIVOS:           $ {total_act}")
        print()
        print("PASIVOS:")
        print(f"  Corrientes:              $ {pas_corr}")
        print(f"  No Corrientes:           $ {pas_no_corr}")
        print(f"  TOTAL PASIVOS:           $ {total_pas}")
        print()
        print("PATRIMONIO:")
        print(f"  Capital:                 $ {capital}")
        print(f"  Utilidades Retenidas:    $ {util_ret}")
        print(f"  Utilidades del Ejercicio:$ {util_ej}")
        print(f"  TOTAL PATRIMONIO:        $ {total_pat}")
        print("-"*70)
        print("RATIOS FINANCIEROS:")
        print(f"Ratio de Liquidez:         {balance['ratio_liquidez']:.2f}")
        print(f"Ratio de Endeudamiento:    {balance['ratio_endeudamiento']:.2f}")
        print(f"Ecuación Contable:         {'✅ Válida' if balance['ecuacion_contable_valida'] else '❌ Inválida'}")
        
        print("="*70)
        print(f"✅ Informe generado en {response.execution_time_seconds:.2f} segundos")
        if response.file_path:
            print(f"📄 Archivo guardado: {response.file_path}")
        print()
    
    def _mostrar_resultado_informe_completo(self, response) -> None:
        """Mostrar resultado del informe financiero completo en consola."""
        if not response.data:
            print("❌ No se pudo obtener datos del informe completo")
            return
        
        print("\n" + "="*80)
        print("                    INFORME FINANCIERO COMPLETO")
        print("="*80)
        
        # Mostrar resumen ejecutivo si está disponible
        if "analisis_financiero" in response.data:
            analisis = response.data["analisis_financiero"]
            resumen = analisis.get("resumen_ejecutivo", {})
            
            print("📊 RESUMEN EJECUTIVO:")
            
            if "rentabilidad" in resumen:
                rent = resumen["rentabilidad"]
                print(f"   Rentabilidad:     {rent['estado']} (Margen Neto: {rent['margen_neto']:.2f}%)")
            
            if "liquidez" in resumen:
                liq = resumen["liquidez"]
                print(f"   Liquidez:         {liq['estado']} (Ratio: {liq['ratio']:.2f})")
            
            if "endeudamiento" in resumen:
                end = resumen["endeudamiento"]
                print(f"   Endeudamiento:    {end['estado']} (Ratio: {end['ratio']:.2f})")
            
            print(f"   Coherencia:       {'✅ Válida' if response.data.get('coherencia_informes', False) else '❌ Inválida'}")
            
            # Mostrar alertas si existen
            if "alertas" in analisis and analisis["alertas"]:
                print("\n🚨 ALERTAS:")
                for alerta in analisis["alertas"]:
                    print(f"   {alerta}")
        
        # Mostrar KPIs principales
        if "kpis_principales" in response.data:
            kpis = response.data["kpis_principales"]
            print("\n📈 KPIs PRINCIPALES:")
            print(f"   ROA (Return on Assets):   {kpis.get('roa', 0):.2f}%")
            print(f"   ROE (Return on Equity):   {kpis.get('roe', 0):.2f}%")
            print(f"   Margen Bruto:             {kpis.get('margen_bruto', 0):.2f}%")
            print(f"   Margen Neto:              {kpis.get('margen_neto', 0):.2f}%")
            print(f"   Ratio Liquidez:           {kpis.get('ratio_liquidez', 0):.2f}")
            print(f"   Ratio Endeudamiento:      {kpis.get('ratio_endeudamiento', 0):.2f}")
        
        print("="*80)
        print(f"✅ Informe completo generado en {response.execution_time_seconds:.2f} segundos")
        if response.file_path:
            print(f"📄 Archivo guardado: {response.file_path}")
        print()
        print("💡 Para ver los informes detallados, consulte el archivo generado.")
        print()
    
    # ========================================================================================
    # MÉTODOS DE UTILIDAD PARA EL SISTEMA PRINCIPAL
    # ========================================================================================
    
    def get_menu_options(self) -> Dict[str, str]:
        """
        Obtener opciones de menú para integrar con el sistema principal.
        
        Returns:
            Diccionario con opciones de menú
        """
        return {
            "estado_resultados": "Generar Estado de Resultados",
            "balance_general": "Generar Estado de Situación Financiera", 
            "informe_completo": "Generar Informe Financiero Completo"
        }
    
    def test_integration(self) -> bool:
        """
        Probar la integración completa de informes financieros.
        
        Returns:
            True si todas las pruebas pasan
        """
        try:
            self._logger.info("Probando integración de informes financieros")
            
            # Probar validaciones
            val_estado = self._service.validar_parametros_estado_resultados("2025-01-01", "2025-01-31")
            val_balance = self._service.validar_parametros_balance_general("2025-01-31")
            
            if not (val_estado['valid'] and val_balance['valid']):
                return False
            
            # Probar obtención de períodos sugeridos
            periodos = self._service.get_tipos_periodo_sugeridos()
            fechas = self._service.get_fechas_corte_sugeridas()
            
            if not (periodos and fechas):
                return False
            
            self._logger.info("Integración de informes financieros probada exitosamente")
            return True
            
        except Exception as e:
            self._logger.error(f"Error probando integración: {str(e)}")
            return False