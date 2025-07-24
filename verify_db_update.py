"""
Verificación rápida de que DatabaseManager se actualizó correctamente
"""

from database.db_manager import DatabaseManager

def verify_update():
    print("🔍 VERIFICANDO ACTUALIZACIÓN DE DATABASE MANAGER...")
    print("=" * 60)
    
    try:
        # Crear instancia
        db = DatabaseManager()
        print("✅ DatabaseManager instanciado correctamente")
        
        # Verificar métodos críticos
        methods_to_check = [
            'obtener_estadisticas',
            'obtener_ejercicios',
            'agregar_ejercicio',
            'actualizar_ejercicio',
            'obtener_ejercicio_por_id',
            'obtener_unidades_tematicas'
        ]
        
        print("\n📋 Verificando métodos:")
        all_good = True
        for method in methods_to_check:
            if hasattr(db, method):
                print(f"  ✅ {method}")
            else:
                print(f"  ❌ {method}")
                all_good = False
        
        if all_good:
            # Probar métodos
            print("\n🧪 Probando funcionalidad:")
            
            # Obtener estadísticas
            stats = db.obtener_estadisticas()
            print(f"  ✅ obtener_estadisticas() - Total ejercicios: {stats['total_ejercicios']}")
            
            # Obtener ejercicios
            ejercicios = db.obtener_ejercicios()
            print(f"  ✅ obtener_ejercicios() - Ejercicios encontrados: {len(ejercicios)}")
            
            # Obtener unidades
            unidades = db.obtener_unidades_tematicas()
            print(f"  ✅ obtener_unidades_tematicas() - Unidades: {len(unidades)}")
            
            print("\n🎉 ¡DatabaseManager actualizado y funcionando correctamente!")
            return True
        else:
            print("\n❌ Faltan algunos métodos")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_update()
    if success:
        print("\n✅ Ahora puedes ejecutar: python test_integration_v3.py")
    else:
        print("\n❌ Revisa el error antes de continuar")